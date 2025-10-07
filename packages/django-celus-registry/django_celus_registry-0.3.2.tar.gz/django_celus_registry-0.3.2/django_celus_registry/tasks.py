import logging
import typing
from functools import partial

import celery
import requests
from django.conf import settings
from django.db import models, transaction
from django.dispatch import Signal

from .models import CounterVersionChoices, Notification, Platform, Report, SushiService
from .serializers import (
    NotificationSerializer,
    PlatformSerializer,
    ReportSerializer,
    SushiServiceSerializer,
)

logger = logging.getLogger(__name__)


registry_changed = Signal()


def get_base_url():
    url = getattr(settings, "CELUS_REGISTRY_URL", "https://registry.countermetrics.org")
    return f"{url}/api/v1/"


def get_or_none(model_class: typing.Type[models.Model], *args, **kwargs):
    try:
        return model_class.objects.get(*args, **kwargs)
    except model_class.DoesNotExist:
        return None


class Change(typing.NamedTuple):
    key: str
    old: typing.Optional[str] = None
    new: typing.Optional[str] = None
    category: bool = False


class PlatformColumn(typing.NamedTuple):
    name: str
    uuid: str


def get_val(obj, key):
    if hasattr(obj, key):
        return getattr(obj, key)
    if hasattr(obj, "get"):
        return obj.get(key)
    return None


class ChangeTracker:
    PRETTY_NAMES = {"abbrev": "short name"}

    def __init__(self):
        self.updated = {}
        self.created = {}
        self.deleted = {}

    @classmethod
    def check_changes(cls, table, platform, fields, prefix, old, new):
        for name in fields:
            if name == "id":
                continue
            val_old = get_val(old, name)
            val_new = get_val(new, name)
            if name == "counter_release" and isinstance(val_new, str):
                val_new = CounterVersionChoices.from_string(val_new)
            if val_old != val_new:
                if prefix:
                    table.setdefault(platform, []).append(Change(prefix, category=True))
                    prefix = None
                name = cls.PRETTY_NAMES.get(name, name.replace("_", " "))
                if name == "reports":
                    added = ", ".join(sorted(val_new - val_old))
                    added = "\n\n+ " + added if added and val_old else ""
                    removed = ", ".join(sorted(val_old - val_new))
                    removed = "\n\n- " + removed if removed and val_new else ""
                    table.setdefault(platform, []).append(
                        Change(
                            name,
                            ", ".join(sorted(val_old)),
                            ", ".join(sorted(val_new)) + added + removed,
                        )
                    )
                else:
                    table.setdefault(platform, []).append(
                        Change(name, val_old, val_new)
                    )

    def platform_wrapper(self, old, new, platform):
        table = self.updated
        if old is None:
            table = self.created
        elif new is None:
            table = self.deleted
        return partial(self.check_changes, table, platform)


@celery.shared_task
@transaction.atomic
def update_registry_models():
    client = requests.Session()
    modified = update_platforms_and_sushi_services(client)
    modified = modified or update_notifications(client)
    if modified:
        logging.info("Registry changed => triggering signal")
        registry_changed.send(__name__)


def update_platforms_and_sushi_services(client: requests.Session):
    logging.info("Starting to download data from registry")

    url = f"{get_base_url()}/platform/"
    resp = client.get(url)
    logging.debug(f"{url} ({resp.status_code})")
    if resp.status_code != 200:
        logging.warning("Unable to download platforms. Terminating")
        return

    data = resp.json()

    seen_platform_ids = set()
    seen_sushi_service_ids = set()

    tracker = ChangeTracker()

    for platform_data in data:
        serializer = PlatformSerializer(
            get_or_none(Platform, pk=platform_data["id"]), data=platform_data
        )
        serializer.is_valid(raise_exception=True)
        track = tracker.platform_wrapper(
            serializer.instance,
            platform_data,
            PlatformColumn(platform_data["name"], platform_data["id"]),
        )
        track(
            (name for name, field in serializer.fields.items() if not field.read_only),
            "",
            serializer.instance,  # == get_or_none()
            serializer.initial_data,  # == platform_data
        )
        platform = serializer.save()
        seen_platform_ids.add(platform.id)

        # fill in and update report types
        reports = []
        for report_data in platform_data.get("reports", []):
            rep_serializer = ReportSerializer(
                get_or_none(
                    Report,
                    report_id=report_data["report_id"],
                    counter_release=CounterVersionChoices.from_string(
                        report_data["counter_release"]
                    ),
                ),
                data=report_data,
            )
            rep_serializer.is_valid(raise_exception=True)
            report = rep_serializer.save()
            reports.append(report)

        track(
            ("reports",),
            "",
            {"reports": set([r.report_id for r in platform.reports.all()])},
            {"reports": set([r.report_id for r in reports])},
        )
        platform.reports.set(reports)

        # fill in and update sushi services
        sushi_services = []
        for sushi_service_link in platform_data.get("sushi_services", []):
            resp = client.get(sushi_service_link["url"])
            if resp.status_code != 200:
                logging.warning(
                    "Unable to download sushi service '%s'", sushi_service_link["url"]
                )
                raise RuntimeError("Failed to download sushi service.")

            logging.debug(
                "%s C%s",
                sushi_service_link["url"],
                sushi_service_link["counter_release"],
            )
            service_data = resp.json()
            ser_serializer = SushiServiceSerializer(
                get_or_none(SushiService, pk=service_data["id"]), data=service_data
            )
            ser_serializer.is_valid(raise_exception=True)
            track(
                (
                    name
                    for name, field in ser_serializer.fields.items()
                    if not field.read_only
                ),
                f"SUSHI - {ser_serializer.initial_data['url']}",
                ser_serializer.instance,  # == get_or_none()
                ser_serializer.initial_data,  # == platform_data
            )
            sushi_service = ser_serializer.save()
            seen_sushi_service_ids.add(sushi_service.id)
            sushi_services.append(sushi_service)
        platform.sushi_services.set(sushi_services)

    # Clean removed
    removed = Platform.objects.exclude(id__in=seen_platform_ids)
    for platform in removed:
        track = tracker.platform_wrapper(
            platform, None, PlatformColumn(platform.name, platform.id)
        )
        track(
            (
                name
                for name, field in PlatformSerializer().fields.items()
                if not field.read_only
            ),
            "",
            platform,
            None,
        )
        track(
            ("reports",),
            "",
            {"reports": set([r.report_id for r in platform.reports.all()])},
            {"reports": set()},
        )
        for sushi in platform.sushi_services.all():
            track(
                (
                    name
                    for name, field in SushiServiceSerializer().fields.items()
                    if not field.read_only
                ),
                f"SUSHI - {sushi.url}",
                sushi,
                None,
            )
    removed.delete()
    SushiService.objects.exclude(id__in=seen_sushi_service_ids).delete()

    if tracker.updated or tracker.deleted or tracker.created:
        registry_changed.send(
            __name__,
            updated=tracker.updated,
            deleted=tracker.deleted,
            created=tracker.created,
        )


def update_notifications(client: requests.Session) -> bool:
    """returns True if notifications were modified"""
    url = f"{get_base_url()}/notification/"
    modified = False
    seen_ids = set()
    while url:
        resp = client.get(url)
        logging.debug(f"{url} ({resp.status_code})")
        if resp.status_code != 200:
            logging.warning("Unable to download notifications. Terminating")
            return
        data = resp.json()
        for notification_data in data.get("results", []):
            seen_ids.add(notification_data["id"])
            if old_object := Notification.objects.filter(
                id=notification_data["id"]
            ).last():
                serializer = NotificationSerializer(old_object, data=notification_data)
                serializer.is_valid(raise_exception=True)
                old_serializer = NotificationSerializer(old_object)
                record_modified = (
                    modified or old_serializer.data != serializer.validated_data
                )
                if record_modified:
                    serializer.save()
            else:
                serializer = NotificationSerializer(data=notification_data)
                serializer.is_valid(raise_exception=True)
                record_modified = True
                # Create new notification
                serializer.save()

            modified = modified or record_modified
            # Update models
            serializer.save()

        url = data.get("next", None)

    # delete removed notifications
    delete_count, _ = Notification.objects.exclude(pk__in=seen_ids).delete()
    return modified or bool(delete_count)
