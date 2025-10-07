from django.db import models
from django.utils import timezone

from utils.models import TimestampedModel
from .manager import device_manager
from .consts import device_type_2_icon_url_map


class ConnectionStatus(models.TextChoices):
    DISCONNECTED = "disconnected", "Disconnected"
    CONNECTING = "connecting", "Connecting"
    CONNECTED = "connected", "Connected"
    FAILED = "failed", "Failed"


class DeviceConnection(TimestampedModel):
    name = models.CharField(max_length=128, unique=True)
    codename = models.CharField(max_length=128)

    connection_type = models.CharField(max_length=128)
    connection_settings = models.JSONField()

    connection_status = models.CharField(
        max_length=20,
        choices=ConnectionStatus.choices,
        default=ConnectionStatus.DISCONNECTED,
    )
    last_connection_attempt = models.DateTimeField(null=True, blank=True)
    last_successful_connection = models.DateTimeField(null=True, blank=True)
    connection_error_message = models.TextField(blank=True, default="")

    def __str__(self):
        return "{} ({})".format(self.name, self.codename)

    def get_device_class(self) -> type["Device"]:
        try:
            return device_manager.get_device_class(self.codename)
        except ValueError:
            return None

    def get_device_type_icon_url(self):
        device_class = self.get_device_class()
        if not device_class:
            return None

        return device_type_2_icon_url_map.get(device_class.device_type)

    def update_connection_status(
        self, status: ConnectionStatus, error_message: str = ""
    ):
        """
        Update the connection status and related timestamps.
        """
        self.connection_status = status
        self.last_connection_attempt = timezone.now()

        if status == ConnectionStatus.CONNECTED:
            self.last_successful_connection = timezone.now()
            self.connection_error_message = ""
        elif status == ConnectionStatus.FAILED:
            self.connection_error_message = error_message

        self.save(
            update_fields=[
                "connection_status",
                "last_connection_attempt",
                "last_successful_connection",
                "connection_error_message",
            ]
        )

    @property
    def is_wifi_connection(self) -> bool:
        """
        Check if this is a WiFi-based connection.
        """
        return self.connection_type == "wifi"

    @property
    def wifi_ssid(self) -> str:
        """
        Get the WiFi SSID from connection settings.
        """
        if self.is_wifi_connection:
            return self.connection_settings.get("ssid", "")
        return ""

    @property
    def wifi_password(self) -> str:
        """
        Get the WiFi password from connection settings.
        """
        if self.is_wifi_connection:
            return self.connection_settings.get("password", "")
        return ""

    def delete(self, *args, **kwargs):
        """
        Override delete to clean up WiFi interface assignments.
        """
        if self.is_wifi_connection:
            from .wireless_interface_manager import wireless_interface_manager

            wireless_interface_manager.release_interface_from_device(self.id)
        super().delete(*args, **kwargs)
