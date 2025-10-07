import logging

import django_rq
from rest_framework import status
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    ListModelMixin,
    CreateModelMixin,
)
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.response import Response

from utils.drf.viewsets import SerializersActionMapMixin
from .exceptions import DeviceConnectionException
from .manager import device_manager
from .models import DeviceConnection
from .utils import get_device_instance
from .tasks import (
    connect_to_device_wifi,
    disconnect_from_device_wifi,
    check_device_connection_status,
    start_periodic_connection_monitoring,
)
from .wireless_interface_manager import wireless_interface_manager
from .serializers import (
    DeviceConnectionCreateSerializer,
    DeviceConnectionSerializer,
    SupportedDeviceSerializer,
)


logger = logging.getLogger(__name__)


class DeviceConnectionViewSet(
    SerializersActionMapMixin,
    GenericViewSet,
    ListModelMixin,
    CreateModelMixin,
):
    serializers_action_map = {
        "list": DeviceConnectionSerializer,
        "create": DeviceConnectionCreateSerializer,
    }
    queryset = DeviceConnection.objects.all()

    @action(detail=False, methods=["GET"], url_path="supported-devices")
    def supported_devices(self, request):
        device_classes = device_manager.get_device_classes()

        return Response(
            {
                "supported_devices": [
                    SupportedDeviceSerializer(instance=device_class).data
                    for device_class in device_classes.values()
                ]
            }
        )

    def _validate_connection_settings(self, device, serializer):
        try:
            errors = device.validate_connection_settings(
                serializer.validated_data["connection_type"],
                serializer.validated_data["connection_settings"],
            )
        except DeviceConnectionException as e:
            raise ValidationError(str(e))

        if errors:
            raise ValidationError(
                {
                    "connection_settings": errors,
                }
            )

    def _verify_connection(self, device, serializer):
        error = None

        try:
            device.check_connectivity()
        except DeviceConnectionException as e:
            error = "Could not connect to device: {}".format(str(e))
        except Exception as e:
            logger.exception("Could not connect to device!")
            error = "Could not connect to device: Unknown error"

        if error:
            # Bind error to the top field of the connection type's parameters
            first_field_name = next(
                iter(
                    serializer.validated_data["connection_settings"],
                )
            )

            raise ValidationError(
                {
                    first_field_name: [error],
                }
            )

    def perform_create(self, serializer):
        device = get_device_instance(
            serializer.validated_data["codename"],
            serializer.validated_data["connection_type"],
            serializer.validated_data["connection_settings"],
        )

        self._validate_connection_settings(device, serializer)
        # self._verify_connection(device, serializer)

        # Save the device connection
        device_connection = serializer.save()

        # Attempt to connect in the background
        if device_connection.is_wifi_connection:
            django_rq.enqueue(connect_to_device_wifi, device_connection.id)

        return device_connection

    @action(detail=False, methods=["GET"], url_path="wifi/connect")
    def connect_wifi(self, request):
        """
        Connect to the device's WiFi network using query parameter.
        """
        device_id = request.query_params.get("device_id")
        if not device_id:
            return Response(
                {"error": "device_id query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            device_connection = DeviceConnection.objects.get(id=device_id)
        except DeviceConnection.DoesNotExist:
            return Response(
                {"error": f"DeviceConnection with ID {device_id} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not device_connection.is_wifi_connection:
            return Response(
                {"error": "This device does not use WiFi connection"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Enqueue the connection task
        django_rq.enqueue(connect_to_device_wifi, device_connection.id)

        return Response(
            {
                "message": f"Connecting to WiFi network for {device_connection.name}",
                "status": "connecting",
            }
        )

    @action(detail=False, methods=["GET"], url_path="wifi/disconnect")
    def disconnect_wifi(self, request):
        """
        Disconnect from the device's WiFi network using query parameter.
        """
        device_id = request.query_params.get("device_id")
        if not device_id:
            return Response(
                {"error": "device_id query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            device_connection = DeviceConnection.objects.get(id=device_id)
        except DeviceConnection.DoesNotExist:
            return Response(
                {"error": f"DeviceConnection with ID {device_id} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not device_connection.is_wifi_connection:
            return Response(
                {"error": "This device does not use WiFi connection"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Enqueue the disconnection task
        django_rq.enqueue(disconnect_from_device_wifi, device_connection.id)

        return Response(
            {
                "message": f"Disconnecting from WiFi network for {device_connection.name}",
                "status": "disconnecting",
            }
        )

    @action(detail=False, methods=["GET"], url_path="wifi/status")
    def connection_status(self, request):
        """
        Get the current connection status for the device using query parameter.
        """
        device_id = request.query_params.get("device_id")
        if not device_id:
            return Response(
                {"error": "device_id query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            device_connection = DeviceConnection.objects.get(id=device_id)
        except DeviceConnection.DoesNotExist:
            return Response(
                {"error": f"DeviceConnection with ID {device_id} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Refresh the connection status
        if device_connection.is_wifi_connection:
            django_rq.enqueue(check_device_connection_status, device_connection.id)

        return Response(
            {
                "device_connection_id": device_connection.id,
                "device_name": device_connection.name,
                "connection_type": device_connection.connection_type,
                "connection_status": device_connection.connection_status,
                "last_connection_attempt": device_connection.last_connection_attempt,
                "last_successful_connection": device_connection.last_successful_connection,
                "connection_error_message": device_connection.connection_error_message,
                "is_wifi_connection": device_connection.is_wifi_connection,
            }
        )

    @action(detail=False, methods=["GET"], url_path="wifi/interfaces")
    def wifi_interfaces(self, request):
        """
        Get WiFi interface information and assignments.
        """
        assignments = wireless_interface_manager.get_interface_assignments()

        return Response(
            {
                "available_interfaces": wireless_interface_manager.get_available_interfaces(),
                "interface_assignments": assignments,
                "total_interfaces": len(
                    wireless_interface_manager.get_available_interfaces()
                ),
                "assigned_interfaces": len(assignments),
            }
        )

    @action(detail=False, methods=["GET"], url_path="wifi/start-monitoring")
    def start_monitoring(self, request):
        """
        Start periodic monitoring of WiFi connections.
        """
        try:
            start_periodic_connection_monitoring()

            return Response(
                {
                    "message": "Started periodic connection monitoring.",
                    "status": "success",
                }
            )
        except Exception as e:
            logger.error(f"Failed to start monitoring: {str(e)}")
            return Response(
                {
                    "error": f"Failed to start monitoring: {str(e)}",
                    "status": "error",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
