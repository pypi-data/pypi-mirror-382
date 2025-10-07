import logging
from datetime import timedelta

import django_rq
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import DeviceConnection, ConnectionStatus
from .wireless_interface_manager import wireless_interface_manager, WiFiConnectionStatus

logger = logging.getLogger(__name__)


def connect_to_device_wifi(device_connection_id: int) -> bool:
    """
    Connect to a device's WiFi network.

    Args:
        device_connection_id: The ID of the DeviceConnection to connect to

    Returns:
        bool: True if connection was successful, False otherwise
    """
    try:
        device_connection = DeviceConnection.objects.get(id=device_connection_id)
    except DeviceConnection.DoesNotExist:
        logger.error(f"DeviceConnection with ID {device_connection_id} not found")
        return False

    if not device_connection.is_wifi_connection:
        logger.error(
            f"DeviceConnection {device_connection_id} is not a WiFi connection"
        )
        return False

    logger.info(f"Connecting to WiFi for device: {device_connection.name}")

    # Update status to connecting
    device_connection.update_connection_status(ConnectionStatus.CONNECTING)

    # Emit status update via WebSocket
    _emit_connection_status_update(device_connection)

    # Attempt to connect
    success, message = wireless_interface_manager.connect_to_wifi(
        device_connection.id,
        device_connection.wifi_ssid,
        device_connection.wifi_password,
    )

    if success:
        device_connection.update_connection_status(ConnectionStatus.CONNECTED)
        logger.info(
            f"Successfully connected to WiFi for device: {device_connection.name}"
        )
    else:
        device_connection.update_connection_status(ConnectionStatus.FAILED, message)
        logger.error(
            f"Failed to connect to WiFi for device {device_connection.name}: {message}"
        )

    # Emit updated status via WebSocket
    _emit_connection_status_update(device_connection)

    return success


def disconnect_from_device_wifi(device_connection_id: int) -> bool:
    """
    Disconnect from a device's WiFi network.

    Args:
        device_connection_id: The ID of the DeviceConnection to disconnect from

    Returns:
        bool: True if disconnection was successful, False otherwise
    """
    try:
        device_connection = DeviceConnection.objects.get(id=device_connection_id)
    except DeviceConnection.DoesNotExist:
        logger.error(f"DeviceConnection with ID {device_connection_id} not found")
        return False

    if not device_connection.is_wifi_connection:
        logger.error(
            f"DeviceConnection {device_connection_id} is not a WiFi connection"
        )
        return False

    logger.info(f"Disconnecting from WiFi for device: {device_connection.name}")

    success, message = wireless_interface_manager.disconnect_from_wifi(
        device_connection.id, device_connection.wifi_ssid
    )

    if success:
        device_connection.update_connection_status(ConnectionStatus.DISCONNECTED)
        logger.info(
            f"Successfully disconnected from WiFi for device: {device_connection.name}"
        )
    else:
        logger.error(
            f"Failed to disconnect from WiFi for device {device_connection.name}: {message}"
        )

    # Emit updated status via WebSocket
    _emit_connection_status_update(device_connection)

    return success


def check_device_connection_status(device_connection_id: int) -> bool:
    """
    Check the current connection status for a device.

    Args:
        device_connection_id: The ID of the DeviceConnection to check

    Returns:
        bool: True if device is connected, False otherwise
    """
    try:
        device_connection = DeviceConnection.objects.get(id=device_connection_id)
    except DeviceConnection.DoesNotExist:
        logger.error(f"DeviceConnection with ID {device_connection_id} not found")
        return False

    if not device_connection.is_wifi_connection:
        return False

    current_status = wireless_interface_manager.check_wifi_connection_status(
        device_connection.id, device_connection.wifi_ssid
    )

    # Convert WiFiConnectionStatus to ConnectionStatus
    if current_status == WiFiConnectionStatus.CONNECTED:
        db_status = ConnectionStatus.CONNECTED
    elif current_status == WiFiConnectionStatus.CONNECTING:
        db_status = ConnectionStatus.CONNECTING
    elif current_status == WiFiConnectionStatus.FAILED:
        db_status = ConnectionStatus.FAILED
    else:
        db_status = ConnectionStatus.DISCONNECTED

    # Only update if status has changed
    if device_connection.connection_status != db_status:
        device_connection.update_connection_status(db_status)
        _emit_connection_status_update(device_connection)
        logger.info(
            f"Connection status updated for {device_connection.name}: {db_status}"
        )

    return current_status == WiFiConnectionStatus.CONNECTED


def monitor_all_device_connections() -> None:
    """
    Check the connection status of all WiFi-enabled devices.
    This task should be run periodically (every 10 seconds).
    """
    logger.debug("Starting device connection monitoring sweep")

    wifi_connections = DeviceConnection.objects.filter(connection_type="wifi")

    for device_connection in wifi_connections:
        try:
            check_device_connection_status(device_connection.id)
        except Exception as e:
            logger.error(
                f"Error checking connection status for device {device_connection.name}: {str(e)}"
            )

    logger.debug(
        f"Device connection monitoring complete. Checked {wifi_connections.count()} devices"
    )


def start_periodic_connection_monitoring() -> None:
    """
    Start periodic monitoring of device connections.
    This schedules the monitoring task to run every 10 seconds using RQ repeat.
    """
    logger.info("Starting periodic device connection monitoring")

    # Cancel any existing monitoring jobs first
    try:
        queue = django_rq.get_queue("default")
        # Clear existing monitoring jobs
        for job in queue.get_jobs():
            if (
                job.func_name
                == "whitebox_plugin_device_manager.tasks.monitor_all_device_connections"
            ):
                job.cancel()
                logger.info(f"Cancelled existing monitoring job: {job.id}")
    except Exception as e:
        logger.warning(f"Error clearing existing jobs: {e}")

    # Schedule the first monitoring task, which will reschedule itself
    queue = django_rq.get_queue("default")
    queue.enqueue_in(
        timedelta(seconds=10),
        monitor_all_device_connections_with_reschedule,
    )

    logger.info("Periodic monitoring scheduled")


def monitor_all_device_connections_with_reschedule() -> None:
    """
    Monitor all device connections and reschedule the next run.
    This creates a self-perpetuating monitoring loop.
    """
    logger.debug("Running periodic device connection monitoring")

    # Run the actual monitoring
    monitor_all_device_connections()

    # Schedule the next run
    queue = django_rq.get_queue("default")
    queue.enqueue_in(
        timedelta(seconds=10),
        monitor_all_device_connections_with_reschedule,
    )

    logger.debug("Next monitoring run scheduled in 10 seconds")


def _emit_connection_status_update(device_connection: DeviceConnection) -> None:
    """
    Emit a connection status update via WebSocket.

    Args:
        device_connection: The DeviceConnection instance to emit status for
    """
    try:
        channel_layer = get_channel_layer()

        # Prepare the status data
        status_data = {
            "device_connection_id": device_connection.id,
            "device_name": device_connection.name,
            "connection_status": device_connection.connection_status,
            "last_connection_attempt": (
                device_connection.last_connection_attempt.isoformat()
                if device_connection.last_connection_attempt
                else None
            ),
            "last_successful_connection": (
                device_connection.last_successful_connection.isoformat()
                if device_connection.last_successful_connection
                else None
            ),
            "connection_error_message": device_connection.connection_error_message,
        }

        # Send to the management consumer group
        async_to_sync(channel_layer.group_send)(
            "management",
            {"type": "device_connection_status_update", "data": status_data},
        )

        logger.debug(
            f"Emitted connection status update for device: {device_connection.name}"
        )

    except Exception as e:
        logger.error(f"Failed to emit connection status update: {str(e)}")
