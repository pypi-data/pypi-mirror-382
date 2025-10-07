from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class CounterVersionChoices(models.IntegerChoices):
    C4 = 4
    C5 = 5
    C51 = 51

    def to_string(self):
        if self == CounterVersionChoices.C4:
            return "4"
        elif self == CounterVersionChoices.C5:
            return "5"
        elif self == CounterVersionChoices.C51:
            return "5.1"

    @classmethod
    def from_string(self, data):
        if data == "4":
            return CounterVersionChoices.C4
        elif data == "5":
            return CounterVersionChoices.C5
        elif data == "5.1":
            return CounterVersionChoices.C51
        raise ValidationError("Wrong counter value")


class Report(models.Model):
    counter_release = models.PositiveSmallIntegerField(
        choices=CounterVersionChoices.choices
    )
    report_id = models.CharField(max_length=20)

    class Meta:
        unique_together = ("counter_release", "report_id")

    def __str__(self):
        return f"{self.report_id} (C{self.counter_release})"


class Platform(models.Model):
    id = models.UUIDField(primary_key=True)  # noqa
    name = models.CharField(max_length=400)
    abbrev = models.CharField(max_length=50, blank=True)
    content_provider_name = models.CharField(max_length=400, blank=True, null=True)  # noqa
    website = models.URLField(blank=True, null=True)  # noqa
    reports = models.ManyToManyField(
        Report, through="ReportToPlatform", related_name="platforms"
    )

    def __str__(self):
        if self.abbrev:
            return f"{self.name} ({self.abbrev})"
        else:
            return self.name

    @property
    def registry_url(self):
        base_url = getattr(
            settings, "CELUS_REGISTRY_URL", "https://registry.countermetrics.org"
        )
        return f"{base_url}/platform/{self.pk}"


class SushiService(models.Model):
    id = models.UUIDField(primary_key=True)  # noqa
    counter_release = models.PositiveSmallIntegerField(
        choices=CounterVersionChoices.choices
    )
    url = models.URLField(null=True, blank=True)  # noqa
    platform = models.ForeignKey(
        Platform, on_delete=models.SET_NULL, related_name="sushi_services", null=True
    )
    ip_address_authorization = models.BooleanField(
        null=True, blank=True, help_text="Access restricted based on IP address"
    )
    api_key_required = models.BooleanField(
        null=True, blank=True, help_text="Is api key required"
    )
    platform_attr_required = models.BooleanField(
        null=True, blank=True, help_text="Is platform attr required"
    )
    requestor_id_required = models.BooleanField(
        null=True, blank=True, help_text="Is requestor_id required"
    )

    def __str__(self):
        return f"{self.url or ''} (C{self.counter_release})"


class ReportToPlatform(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)

    def __str__(self):
        return type(self).__name__


class Notification(models.Model):
    # TODO linked ReportViews
    # TODO linked UsageDataHost

    id = models.UUIDField(primary_key=True)
    source = models.CharField(max_length=16)
    type = models.CharField(max_length=12)
    sushi_service = models.ForeignKey(
        SushiService,
        on_delete=models.CASCADE,
        related_name="notifications",
        blank=True,
        null=True,
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    subject = models.CharField(max_length=128)
    message = models.TextField(blank=True)
    published_date = models.DateTimeField(
        blank=True, null=True, help_text="When the notification was published"
    )
    last_modified = models.DateTimeField()
    reports = models.JSONField(default=list)
