from unittest.mock import Mock, patch
from unittest import TestCase

from whitebox_plugin_device_manager.wireless_interface_manager import (
    WirelessInterfaceManager,
    WiFiConnectionStatus,
)


class TestWirelessInterfaceManager(TestCase):
    def setUp(self):
        # Reset singleton state between tests
        WirelessInterfaceManager._instance = None
        WirelessInterfaceManager._initialized = False

    @patch("subprocess.run")
    @patch("pathlib.Path.exists")
    def test_discover_wifi_interfaces(self, mock_exists, mock_subprocess_run):
        mock_exists.return_value = False
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = (
            "DEVICE  TYPE      STATE\n"
            "wlan0   wifi      connected\n"
            "wlan1   wifi      disconnected\n"
            "wlan2   wifi      disconnected\n"
            "eth0    ethernet  connected\n"
        )
        mock_subprocess_run.return_value = mock_result

        manager = WirelessInterfaceManager()

        # wlan0 should be excluded
        self.assertNotIn("wlan0", manager.available_interfaces)
        self.assertIn("wlan1", manager.available_interfaces)
        self.assertIn("wlan2", manager.available_interfaces)
        self.assertEqual(len(manager.available_interfaces), 2)

    @patch("subprocess.run")
    @patch("pathlib.Path.exists")
    def test_assign_interface_to_device(self, mock_exists, mock_subprocess_run):
        mock_exists.return_value = False
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = (
            "DEVICE  TYPE      STATE\n"
            "wlan1   wifi      disconnected\n"
            "wlan2   wifi      disconnected\n"
        )
        mock_subprocess_run.return_value = mock_result

        manager = WirelessInterfaceManager()

        with patch.object(manager, "_save_to_file"):
            interface = manager.assign_interface_to_device(1)

        self.assertEqual(interface, "wlan1")
        self.assertEqual(manager.device_interface_map[1], "wlan1")
        self.assertEqual(manager.interface_device_map["wlan1"], 1)

    @patch("subprocess.run")
    @patch("pathlib.Path.exists")
    def test_assign_interface_already_assigned(self, mock_exists, mock_subprocess_run):
        mock_exists.return_value = False
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = (
            "DEVICE  TYPE      STATE\n" "wlan1   wifi      disconnected\n"
        )
        mock_subprocess_run.return_value = mock_result

        manager = WirelessInterfaceManager()

        with patch.object(manager, "_save_to_file"):
            interface1 = manager.assign_interface_to_device(1)
            interface2 = manager.assign_interface_to_device(1)

        self.assertEqual(interface1, interface2)

    @patch("subprocess.run")
    @patch("pathlib.Path.exists")
    def test_release_interface_from_device(self, mock_exists, mock_subprocess_run):
        mock_exists.return_value = False
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = (
            "DEVICE  TYPE      STATE\n" "wlan1   wifi      disconnected\n"
        )
        mock_subprocess_run.return_value = mock_result

        manager = WirelessInterfaceManager()

        with patch.object(manager, "_save_to_file"):
            manager.assign_interface_to_device(1)
            result = manager.release_interface_from_device(1)

        self.assertTrue(result)
        self.assertNotIn(1, manager.device_interface_map)
        self.assertNotIn("wlan1", manager.interface_device_map)

    @patch("subprocess.run")
    @patch("pathlib.Path.exists")
    def test_connect_to_wifi_success(self, mock_exists, mock_subprocess_run):
        mock_exists.return_value = False

        # First call for interface discovery
        discovery_result = Mock()
        discovery_result.returncode = 0
        discovery_result.stdout = (
            "DEVICE  TYPE      STATE\n" "wlan1   wifi      disconnected\n"
        )

        # Second call for connection
        connect_result = Mock()
        connect_result.returncode = 0
        connect_result.stdout = "Connection activated"

        mock_subprocess_run.side_effect = [discovery_result, connect_result]

        manager = WirelessInterfaceManager()

        with patch.object(manager, "_save_to_file"):
            success, message = manager.connect_to_wifi(1, "test_ssid", "test_pass")

        self.assertTrue(success)
        self.assertIn("Connected", message)

    @patch("subprocess.run")
    @patch("pathlib.Path.exists")
    def test_connect_to_wifi_failure(self, mock_exists, mock_subprocess_run):
        mock_exists.return_value = False

        # First call for interface discovery
        discovery_result = Mock()
        discovery_result.returncode = 0
        discovery_result.stdout = (
            "DEVICE  TYPE      STATE\n" "wlan1   wifi      disconnected\n"
        )

        # Second call for connection fails
        connect_result = Mock()
        connect_result.returncode = 1
        connect_result.stderr = "Connection failed"

        mock_subprocess_run.side_effect = [discovery_result, connect_result]

        manager = WirelessInterfaceManager()

        with patch.object(manager, "_save_to_file"):
            success, message = manager.connect_to_wifi(1, "test_ssid", "test_pass")

        self.assertFalse(success)
        self.assertIn("failed", message.lower())

    @patch("subprocess.run")
    @patch("pathlib.Path.exists")
    def test_check_wifi_connection_status_connected(
        self, mock_exists, mock_subprocess_run
    ):
        mock_exists.return_value = False

        # First call for interface discovery
        discovery_result = Mock()
        discovery_result.returncode = 0
        discovery_result.stdout = (
            "DEVICE  TYPE      STATE\n" "wlan1   wifi      disconnected\n"
        )

        # Second call for status check
        status_result = Mock()
        status_result.returncode = 0
        status_result.stdout = "test_ssid:wlan1:activated\n"

        mock_subprocess_run.side_effect = [discovery_result, status_result]

        manager = WirelessInterfaceManager()

        with patch.object(manager, "_save_to_file"):
            manager.assign_interface_to_device(1)

        status = manager.check_wifi_connection_status(1, "test_ssid")

        self.assertEqual(status, WiFiConnectionStatus.CONNECTED)

    @patch("subprocess.run")
    @patch("pathlib.Path.exists")
    def test_check_wifi_connection_status_disconnected(
        self, mock_exists, mock_subprocess_run
    ):
        mock_exists.return_value = False

        # First call for interface discovery
        discovery_result = Mock()
        discovery_result.returncode = 0
        discovery_result.stdout = (
            "DEVICE  TYPE      STATE\n" "wlan1   wifi      disconnected\n"
        )

        # Second call for status check
        status_result = Mock()
        status_result.returncode = 0
        status_result.stdout = ""

        mock_subprocess_run.side_effect = [discovery_result, status_result]

        manager = WirelessInterfaceManager()

        with patch.object(manager, "_save_to_file"):
            manager.assign_interface_to_device(1)

        status = manager.check_wifi_connection_status(1, "test_ssid")

        self.assertEqual(status, WiFiConnectionStatus.DISCONNECTED)
