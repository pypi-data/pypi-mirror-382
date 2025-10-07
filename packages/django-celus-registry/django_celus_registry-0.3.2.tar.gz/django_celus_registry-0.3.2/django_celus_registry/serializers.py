from datetime import timezone

from rest_framework import serializers

from .models import CounterVersionChoices, Notification, Platform, Report, SushiService


class CounterReleaseField(serializers.Field):
    def to_representation(self, value):
        if isinstance(value, str):
            value = CounterVersionChoices.from_string(value)
        return value.to_string()

    def to_internal_value(self, data):
        return CounterVersionChoices.from_string(data)


class SushiServiceSerializer(serializers.ModelSerializer):
    counter_release = CounterReleaseField()

    class Meta:
        model = SushiService
        fields = (
            "id",
            "counter_release",
            "url",
            "ip_address_authorization",
            "api_key_required",
            "platform_attr_required",
            "requestor_id_required",
        )


class ShortSushiServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SushiService
        fields = ("id",)


class ReportSerializer(serializers.ModelSerializer):
    counter_release = CounterReleaseField()

    class Meta:
        model = Report
        fields = ("counter_release", "report_id")


class PlatformSerializer(serializers.ModelSerializer):
    reports = SushiServiceSerializer(many=True, read_only=True)
    sushi_services = serializers.ListField(child=serializers.URLField(), read_only=True)

    class Meta:
        model = Platform
        fields = (
            "id",
            "name",
            "abbrev",
            "reports",
            "content_provider_name",
            "website",
            "sushi_services",
        )


class NotificationSerializer(serializers.ModelSerializer):
    sushi_service = ShortSushiServiceSerializer()
    last_modified = serializers.DateTimeField(
        format="%Y-%m-%dT%H:%M:%S.%fZ", default_timezone=timezone.utc
    )
    published_date = serializers.DateTimeField(
        format="%Y-%m-%dT%H:%M:%S.%fZ", default_timezone=timezone.utc
    )
    reports = ReportSerializer(many=True)

    class Meta:
        model = Notification
        fields = (
            "id",
            "published_date",
            "last_modified",
            "source",
            "type",
            "start_date",
            "end_date",
            "sushi_service",
            "subject",
            "message",
            "reports",
        )

    def convert_sushi_service_data(self, data):
        if sushi_service_data := data.pop("sushi_service"):
            data["sushi_service_id"] = sushi_service_data["id"]

        return data

    def to_internal_value(self, data):
        # For now we ignore data_host fields
        data.pop("data_host")
        return self.convert_sushi_service_data(data)

    def to_representation(self, instance):
        res = super().to_representation(instance)
        return self.convert_sushi_service_data(res)
