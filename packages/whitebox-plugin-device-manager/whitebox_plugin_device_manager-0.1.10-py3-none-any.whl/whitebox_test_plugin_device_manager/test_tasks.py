from unittest.mock import Mock, patch
from django.test import TestCase

from whitebox_plugin_device_manager.tasks import (
    connect_to_device_wifi,
    disconnect_from_device_wifi,
    check_device_connection_status,
    monitor_all_device_connections,
    _emit_connection_status_update,
)
from whitebox_plugin_device_manager.models import ConnectionStatus
from whitebox_plugin_device_manager.wireless_interface_manager import (
    WiFiConnectionStatus,
)


class TestTasks(TestCase):
    def setUp(self):
        self.mock_device_connection = Mock()
        self.mock_device_connection.id = 1
        self.mock_device_connection.name = "Test Camera"
        self.mock_device_connection.is_wifi_connection = True
        self.mock_device_connection.wifi_ssid = "camera_wifi"
        self.mock_device_connection.wifi_password = "password123"
        self.mock_device_connection.connection_status = ConnectionStatus.DISCONNECTED

    @patch("whitebox_plugin_device_manager.tasks.wireless_interface_manager")
    @patch("whitebox_plugin_device_manager.tasks.DeviceConnection")
    @patch("whitebox_plugin_device_manager.tasks._emit_connection_status_update")
    def test_connect_to_device_wifi_success(self, mock_emit, mock_dc_model, mock_wim):
        mock_dc_model.objects.get.return_value = self.mock_device_connection
        mock_wim.connect_to_wifi.return_value = (True, "Connected")

        result = connect_to_device_wifi(1)

        self.assertTrue(result)
        mock_dc_model.objects.get.assert_called_once_with(id=1)
        mock_wim.connect_to_wifi.assert_called_once_with(
            1, "camera_wifi", "password123"
        )
        self.mock_device_connection.update_connection_status.assert_called()
        mock_emit.assert_called()

    @patch("whitebox_plugin_device_manager.tasks.DeviceConnection")
    def test_connect_to_device_wifi_not_found(self, mock_dc_model):
        mock_dc_model.objects.get.side_effect = mock_dc_model.DoesNotExist

        result = connect_to_device_wifi(999)

        self.assertFalse(result)

    @patch("whitebox_plugin_device_manager.tasks.DeviceConnection")
    def test_connect_to_device_wifi_not_wifi_connection(self, mock_dc_model):
        self.mock_device_connection.is_wifi_connection = False
        mock_dc_model.objects.get.return_value = self.mock_device_connection

        result = connect_to_device_wifi(1)

        self.assertFalse(result)

    @patch("whitebox_plugin_device_manager.tasks.wireless_interface_manager")
    @patch("whitebox_plugin_device_manager.tasks.DeviceConnection")
    @patch("whitebox_plugin_device_manager.tasks._emit_connection_status_update")
    def test_disconnect_from_device_wifi_success(
        self, mock_emit, mock_dc_model, mock_wim
    ):
        mock_dc_model.objects.get.return_value = self.mock_device_connection
        mock_wim.disconnect_from_wifi.return_value = (True, "Disconnected")

        result = disconnect_from_device_wifi(1)

        self.assertTrue(result)
        mock_wim.disconnect_from_wifi.assert_called_once_with(1, "camera_wifi")
        mock_emit.assert_called()

    @patch("whitebox_plugin_device_manager.tasks.wireless_interface_manager")
    @patch("whitebox_plugin_device_manager.tasks.DeviceConnection")
    @patch("whitebox_plugin_device_manager.tasks._emit_connection_status_update")
    def test_check_device_connection_status(self, mock_emit, mock_dc_model, mock_wim):
        mock_dc_model.objects.get.return_value = self.mock_device_connection
        mock_wim.check_wifi_connection_status.return_value = (
            WiFiConnectionStatus.CONNECTED
        )

        result = check_device_connection_status(1)

        self.assertTrue(result)
        mock_wim.check_wifi_connection_status.assert_called_once_with(1, "camera_wifi")

    @patch("whitebox_plugin_device_manager.tasks.check_device_connection_status")
    @patch("whitebox_plugin_device_manager.tasks.DeviceConnection")
    def test_monitor_all_device_connections(self, mock_dc_model, mock_check_status):
        mock_device_1 = Mock()
        mock_device_1.id = 1
        mock_device_2 = Mock()
        mock_device_2.id = 2

        # Create a mock queryset that supports both iteration and count()
        mock_devices_queryset = Mock()
        mock_devices_queryset.__iter__ = Mock(
            return_value=iter([mock_device_1, mock_device_2])
        )
        mock_devices_queryset.count = Mock(return_value=2)

        mock_queryset = Mock()
        mock_queryset.filter.return_value = mock_devices_queryset
        mock_dc_model.objects = mock_queryset

        monitor_all_device_connections()

        self.assertEqual(mock_check_status.call_count, 2)
        mock_check_status.assert_any_call(1)
        mock_check_status.assert_any_call(2)

    @patch("whitebox_plugin_device_manager.tasks.get_channel_layer")
    @patch("whitebox_plugin_device_manager.tasks.async_to_sync")
    def test_emit_connection_status_update(
        self, mock_async_to_sync, mock_get_channel_layer
    ):
        mock_send = Mock()
        mock_async_to_sync.return_value = mock_send
        mock_channel_layer = Mock()
        mock_get_channel_layer.return_value = mock_channel_layer

        self.mock_device_connection.last_connection_attempt = None
        self.mock_device_connection.last_successful_connection = None
        self.mock_device_connection.connection_error_message = None

        _emit_connection_status_update(self.mock_device_connection)

        mock_async_to_sync.assert_called_once()
        mock_send.assert_called_once()
