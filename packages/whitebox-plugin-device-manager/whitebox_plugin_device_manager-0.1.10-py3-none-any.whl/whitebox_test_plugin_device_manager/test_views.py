from unittest.mock import patch

from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient

from whitebox_plugin_device_manager.base import (
    Device,
    DeviceWizard,
)
from whitebox_plugin_device_manager.exceptions import DeviceConnectionException
from whitebox_plugin_device_manager.manager import device_manager
from whitebox_plugin_device_manager.models import DeviceConnection
from tests.test_utils import DeviceClassResetTestMixin, SupressHTTPErrorLoggingMixin


class TestDeviceWizard(DeviceWizard):
    wizard_step_config = []

    @classmethod
    def get_connection_types(cls) -> dict:
        return {
            "wifi": {
                "name": "Wi-Fi",
                "fields": {
                    "ssid": {
                        "name": "Network Name",
                        "type": "text",
                        "required": True,
                    },
                    "password": {
                        "name": "Network Password",
                        "type": "password",
                        "required": True,
                    },
                },
            },
        }


class TestDevice(Device):
    codename = "device_impersonat0r_9000"
    device_name = "Device Impersonat0r 9000"
    wizard_class = TestDeviceWizard

    @classmethod
    def validate_connection_settings(cls, connection_type, connection_options):
        # No errors by default
        return None

    @classmethod
    def get_connection_types(cls) -> dict:
        return {
            "wifi": {
                "name": "Wi-Fi",
                "fields": {
                    "ssid": {
                        "name": "Network Name",
                        "type": "text",
                        "required": True,
                    },
                    "password": {
                        "name": "Network Password",
                        "type": "password",
                        "required": True,
                    },
                },
            },
        }

    def check_connectivity(self) -> bool:
        return True


global original_device_classes


class TestDeviceViewSet(
    SupressHTTPErrorLoggingMixin,
    DeviceClassResetTestMixin,
    TestCase,
):
    def setUp(self):
        super().setUp()
        device_manager.register_device(TestDevice.codename, TestDevice)
        self.client = APIClient()

    def test_list_supported_devices(self):
        # GIVEN a user is listing all supported devices
        url = reverse("whitebox_plugin_device_manager:device-supported-devices")
        all_device_classes = device_manager.get_device_classes()

        # WHEN the user sends a GET request to the supported devices endpoint
        response = self.client.get(url)

        # THEN the response should be successful and return a list of supported devices
        self.assertEqual(response.status_code, 200)

        device_list = response.json()["supported_devices"]
        for device in device_list:
            codename = device["codename"]
            self.assertIn(codename, all_device_classes)

            device_class = all_device_classes[codename]
            self.assertEqual(device["device_name"], device_class.device_name)
            self.assertEqual(
                device["connection_types"],
                device_class.get_connection_types(),
            )

    def test_list_devices_no_devices(self):
        # GIVEN a user is listing all devices and there are no devices
        url = reverse("whitebox_plugin_device_manager:device-list")

        # WHEN the user sends a GET request to the device list endpoint
        response = self.client.get(url)

        # THEN the response should be successful and return an empty list
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_list_devices_with_devices(self):
        # GIVEN a user is listing all devices and there are devices
        url = reverse("whitebox_plugin_device_manager:device-list")

        device = DeviceConnection.objects.create(
            name="Hubble",
            codename="telescope_interface_wrapper",
            connection_type="antenna",
            connection_settings={
                "test_param": "test_value",
            },
        )

        # WHEN the user sends a GET request to the device list endpoint
        response = self.client.get(url)

        # THEN the response should be successful and return a list of devices
        self.assertEqual(response.status_code, 200)

        expected_response = [
            {
                "id": device.id,
                "name": device.name,
                "codename": device.codename,
                "device_type_icon_url": None,
            }
        ]
        self.assertEqual(response.json(), expected_response)

    @patch("whitebox_plugin_device_manager.views.django_rq.enqueue")
    def test_create_device(self, mock_enqueue):
        # GIVEN a user is creating a device that is supported, e.g. Insta360X4
        url = reverse("whitebox_plugin_device_manager:device-list")
        data = {
            "name": "My new camera",
            "codename": "device_impersonat0r_9000",
            "connection_type": "wifi",
            "connection_settings": {
                "ssid": "my_ssid",
                "password": "my_password",
            },
        }

        # WHEN the user sends a POST request to the device list endpoint
        response = self.client.post(url, data=data, format="json")

        # THEN the response should be successful and the created device was returned
        # Note: _verify_connection is currently commented out in views.py
        self.assertEqual(response.status_code, 201)
        mock_enqueue.assert_called_once()

        device = DeviceConnection.objects.get(id=response.json()["id"])
        expected = {
            "id": device.id,
            "name": device.name,
            "codename": device.codename,
        }
        for key, value in expected.items():
            self.assertEqual(response.json()[key], value)

    def test_create_device_with_unsupported_codename(self):
        # GIVEN a user is creating a device
        url = reverse("whitebox_plugin_device_manager:device-list")
        data = {
            "name": "James Webb",
            "codename": "telescope_interface_wrapper",
            "connection_type": "antenna",
            "connection_settings": {},
        }

        # WHEN the user sends a POST request to the device list endpoint
        response = self.client.post(url, data=data, format="json")

        # THEN the response should be a 400 Bad Request, indicating that the
        #      device codename is invalid
        self.assertEqual(response.status_code, 400)

        self.assertIn("codename", response.json())
        self.assertEqual(
            response.json()["codename"][0],
            "Invalid device codename.",
        )

    def test_create_device_with_unsupported_connection_type(self):
        # GIVEN a user is creating a device
        url = reverse("whitebox_plugin_device_manager:device-list")
        data = {
            "codename": "device_impersonat0r_9000",
            "connection_type": "flux_capacitor",
            "connection_settings": {},
        }

        # WHEN the user sends a POST request to the device list endpoint
        response = self.client.post(url, data=data, format="json")

        # THEN the response should be a 400 Bad Request, indicating that the
        #      connection type is invalid
        self.assertEqual(response.status_code, 400)

        self.assertIn("connection_type", response.json())
        self.assertEqual(
            response.json()["connection_type"][0],
            "Invalid connection type for the device.",
        )

    @patch("whitebox_plugin_device_manager.views.django_rq.enqueue")
    def test_create_device_with_known_error(self, mock_enqueue):
        # GIVEN a user is creating a device
        codename = "device_impersonat0r_9000"
        connection_type = "wifi"
        device_class = device_manager.get_device_class(codename)

        connection_types = device_class.get_connection_types()
        connection_fields = connection_types[connection_type]["fields"]
        first_connection_field = next(iter(connection_fields))

        expected_error_message = "helloworld.exe"

        url = reverse("whitebox_plugin_device_manager:device-list")
        data = {
            "codename": codename,
            "connection_type": connection_type,
            "connection_settings": {
                "ssid": "my_ssid",
                "password": "my_password",
            },
        }

        # Note: _verify_connection is currently commented out in views.py,
        # so connectivity errors are not caught during device creation.
        # The device will be created successfully and connection will be
        # attempted in the background via django_rq.
        # This test is kept for when _verify_connection is re-enabled.
        with patch.object(
            device_class,
            "check_connectivity",
            side_effect=DeviceConnectionException(expected_error_message),
        ):
            response = self.client.post(url, data=data, format="json")

        # Device is created successfully since _verify_connection is commented out
        self.assertEqual(response.status_code, 201)
        mock_enqueue.assert_called_once()

    @patch("whitebox_plugin_device_manager.views.django_rq.enqueue")
    def test_create_device_with_unknown_error(self, mock_enqueue):
        # GIVEN a user is creating a device
        codename = "device_impersonat0r_9000"
        connection_type = "wifi"
        device_class = device_manager.get_device_class(codename)

        connection_types = device_class.get_connection_types()
        connection_fields = connection_types[connection_type]["fields"]
        first_connection_field = next(iter(connection_fields))

        url = reverse("whitebox_plugin_device_manager:device-list")
        data = {
            "codename": codename,
            "connection_type": connection_type,
            "connection_settings": {
                "ssid": "my_ssid",
                "password": "my_password",
            },
        }

        # Note: _verify_connection is currently commented out in views.py,
        # so connectivity errors are not caught during device creation.
        # The device will be created successfully and connection will be
        # attempted in the background via django_rq.
        # This test is kept for when _verify_connection is re-enabled.
        with (
            patch.object(
                device_class,
                "check_connectivity",
                side_effect=Exception("Random Exception"),
            ),
            # Avoid spam in test output
            patch("logging.Logger.exception"),
        ):
            response = self.client.post(url, data=data, format="json")

        # Device is created successfully since _verify_connection is commented out
        self.assertEqual(response.status_code, 201)
        mock_enqueue.assert_called_once()

    @patch("whitebox_plugin_device_manager.views.django_rq.enqueue")
    def test_connect_wifi(self, mock_enqueue):
        # GIVEN a WiFi device connection
        device = DeviceConnection.objects.create(
            name="Test Camera",
            codename="device_impersonat0r_9000",
            connection_type="wifi",
            connection_settings={
                "ssid": "camera_wifi",
                "password": "password123",
            },
        )

        url = reverse("whitebox_plugin_device_manager:device-connect-wifi")

        # WHEN the user sends a request to connect
        response = self.client.get(f"{url}?device_id={device.id}")

        # THEN the response should be successful
        self.assertEqual(response.status_code, 200)
        mock_enqueue.assert_called_once()

    @patch("whitebox_plugin_device_manager.views.django_rq.enqueue")
    def test_connect_wifi_missing_device_id(self, mock_enqueue):
        url = reverse("whitebox_plugin_device_manager:device-connect-wifi")

        # WHEN the user sends a request without device_id
        response = self.client.get(url)

        # THEN the response should be 400
        self.assertEqual(response.status_code, 400)
        mock_enqueue.assert_not_called()

    @patch("whitebox_plugin_device_manager.views.django_rq.enqueue")
    def test_disconnect_wifi(self, mock_enqueue):
        # GIVEN a WiFi device connection
        device = DeviceConnection.objects.create(
            name="Test Camera",
            codename="device_impersonat0r_9000",
            connection_type="wifi",
            connection_settings={
                "ssid": "camera_wifi",
                "password": "password123",
            },
        )

        url = reverse("whitebox_plugin_device_manager:device-disconnect-wifi")

        # WHEN the user sends a request to disconnect
        response = self.client.get(f"{url}?device_id={device.id}")

        # THEN the response should be successful
        self.assertEqual(response.status_code, 200)
        mock_enqueue.assert_called_once()

    @patch("whitebox_plugin_device_manager.views.django_rq.enqueue")
    def test_connection_status(self, mock_enqueue):
        # GIVEN a WiFi device connection
        device = DeviceConnection.objects.create(
            name="Test Camera",
            codename="device_impersonat0r_9000",
            connection_type="wifi",
            connection_settings={
                "ssid": "camera_wifi",
                "password": "password123",
            },
        )

        url = reverse("whitebox_plugin_device_manager:device-connection-status")

        # WHEN the user requests connection status
        response = self.client.get(f"{url}?device_id={device.id}")

        # THEN the response should contain status information
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["device_connection_id"], device.id)
        self.assertEqual(data["device_name"], device.name)
        self.assertTrue(data["is_wifi_connection"])

    @patch("whitebox_plugin_device_manager.views.wireless_interface_manager")
    def test_wifi_interfaces(self, mock_wim):
        # GIVEN available WiFi interfaces
        mock_wim.get_available_interfaces.return_value = ["wlan1", "wlan2"]
        mock_wim.get_interface_assignments.return_value = {1: "wlan1"}

        url = reverse("whitebox_plugin_device_manager:device-wifi-interfaces")

        # WHEN the user requests interface information
        response = self.client.get(url)

        # THEN the response should contain interface data
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total_interfaces"], 2)
        self.assertEqual(data["assigned_interfaces"], 1)

    @patch("whitebox_plugin_device_manager.views.start_periodic_connection_monitoring")
    def test_start_monitoring(self, mock_start_monitoring):
        url = reverse("whitebox_plugin_device_manager:device-start-monitoring")

        # WHEN the user starts monitoring
        response = self.client.get(url)

        # THEN the response should be successful
        self.assertEqual(response.status_code, 200)
        mock_start_monitoring.assert_called_once()
