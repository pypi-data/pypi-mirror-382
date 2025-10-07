from unittest.mock import patch
from django.test import TestCase
from django.utils import timezone

from whitebox_plugin_device_manager.base import Device
from whitebox_plugin_device_manager.consts import DeviceType, device_type_2_icon_url_map
from whitebox_plugin_device_manager.manager import device_manager
from whitebox_plugin_device_manager.models import DeviceConnection, ConnectionStatus
from tests.test_utils import DeviceClassResetTestMixin


class TestDevice1(Device):
    codename = "some_camera"
    device_type = DeviceType.CAMERA_360


class TestDevice2(Device):
    codename = "some_drone"


class TestDeviceConnection(DeviceClassResetTestMixin, TestCase):
    def test_get_device_class(self):
        # GIVEN device connection objects that reference registered devices
        device_manager.register_device(TestDevice1.codename, TestDevice1)
        device_manager.register_device(TestDevice2.codename, TestDevice2)

        connection1 = DeviceConnection(codename=TestDevice1.codename)
        connection2 = DeviceConnection(codename=TestDevice2.codename)
        # Test a connection with a device class that is not registered for
        # situations where it might have originated from a plugin that is
        # currently not loaded
        connection3 = DeviceConnection(codename="does_not_exist")

        # WHEN calling the get_device_class method
        device_class1 = connection1.get_device_class()
        device_class2 = connection2.get_device_class()
        device_class3 = connection3.get_device_class()

        # THEN the method should return the correct device class
        self.assertEqual(device_class1, TestDevice1)
        self.assertEqual(device_class2, TestDevice2)
        self.assertIsNone(device_class3)

    def test_get_device_type_icon_url(self):
        # GIVEN device connection objects that reference registered devices,
        #       with and without an icon
        device_manager.register_device(TestDevice1.codename, TestDevice1)
        device_manager.register_device(TestDevice2.codename, TestDevice2)

        connection1 = DeviceConnection(codename=TestDevice1.codename)
        connection2 = DeviceConnection(codename=TestDevice2.codename)
        # Test a connection with a device class that is not registered for
        # situations where it might have originated from a plugin that is
        # currently not loaded
        connection3 = DeviceConnection(codename="does_not_exist")

        # WHEN calling the get_device_class method
        device_icon1 = connection1.get_device_type_icon_url()
        device_icon2 = connection2.get_device_type_icon_url()
        device_icon3 = connection3.get_device_type_icon_url()

        # THEN the method should return the correct device class
        self.assertEqual(
            device_icon1,
            device_type_2_icon_url_map[TestDevice1.device_type],
        )
        self.assertIsNone(device_icon2)
        self.assertIsNone(device_icon3)

    def test_is_wifi_connection(self):
        # GIVEN device connections with different connection types
        wifi_connection = DeviceConnection(
            codename="test_device",
            connection_type="wifi",
            connection_settings={"ssid": "test", "password": "pass"},
        )
        other_connection = DeviceConnection(
            codename="test_device",
            connection_type="usb",
            connection_settings={},
        )

        # THEN is_wifi_connection should return correct values
        self.assertTrue(wifi_connection.is_wifi_connection)
        self.assertFalse(other_connection.is_wifi_connection)

    def test_wifi_ssid_property(self):
        # GIVEN a WiFi device connection
        wifi_connection = DeviceConnection(
            codename="test_device",
            connection_type="wifi",
            connection_settings={"ssid": "my_network", "password": "pass"},
        )

        # THEN wifi_ssid should return the SSID
        self.assertEqual(wifi_connection.wifi_ssid, "my_network")

    def test_wifi_password_property(self):
        # GIVEN a WiFi device connection
        wifi_connection = DeviceConnection(
            codename="test_device",
            connection_type="wifi",
            connection_settings={"ssid": "network", "password": "secret123"},
        )

        # THEN wifi_password should return the password
        self.assertEqual(wifi_connection.wifi_password, "secret123")

    def test_update_connection_status_connected(self):
        # GIVEN a device connection
        connection = DeviceConnection.objects.create(
            name="Test Device",
            codename="test_device",
            connection_type="wifi",
            connection_settings={"ssid": "test", "password": "pass"},
        )

        # WHEN updating status to CONNECTED
        connection.update_connection_status(ConnectionStatus.CONNECTED)

        # THEN the status and timestamps should be updated
        connection.refresh_from_db()
        self.assertEqual(connection.connection_status, ConnectionStatus.CONNECTED)
        self.assertIsNotNone(connection.last_connection_attempt)
        self.assertIsNotNone(connection.last_successful_connection)
        self.assertEqual(connection.connection_error_message, "")

    def test_update_connection_status_failed(self):
        # GIVEN a device connection
        connection = DeviceConnection.objects.create(
            name="Test Device",
            codename="test_device",
            connection_type="wifi",
            connection_settings={"ssid": "test", "password": "pass"},
        )

        # WHEN updating status to FAILED with error message
        error_msg = "Connection timeout"
        connection.update_connection_status(ConnectionStatus.FAILED, error_msg)

        # THEN the status and error message should be updated
        connection.refresh_from_db()
        self.assertEqual(connection.connection_status, ConnectionStatus.FAILED)
        self.assertIsNotNone(connection.last_connection_attempt)
        self.assertEqual(connection.connection_error_message, error_msg)

    def test_delete_wifi_connection(self):
        # GIVEN a WiFi device connection
        connection = DeviceConnection.objects.create(
            name="Test Device",
            codename="test_device",
            connection_type="wifi",
            connection_settings={"ssid": "test", "password": "pass"},
        )
        device_id = connection.id

        # WHEN deleting the connection
        with patch(
            "whitebox_plugin_device_manager.wireless_interface_manager.wireless_interface_manager"
        ) as mock_wim:
            connection.delete()

            # THEN wireless interface should be released
            mock_wim.release_interface_from_device.assert_called_once_with(device_id)
