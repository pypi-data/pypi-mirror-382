import logging
import subprocess
import json
import os
from pathlib import Path

from enum import Enum
from typing import Dict, List, Optional, Tuple

from utils.locking import global_lock


logger = logging.getLogger(__name__)


class WiFiConnectionStatus(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    FAILED = "failed"


class WirelessInterfaceManager:
    """
    Manager for wireless interface connections to camera devices.
    This service dynamically detects available WiFi interfaces and maps
    one interface per device connection, excluding wlan0 (used for hotspot).
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WirelessInterfaceManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if WirelessInterfaceManager._initialized:
            return

        # Even after implementing singleton pattern, interface assignments
        # won't persist. Hence, we are using a simple JSON file to store
        # cache file to persist interface assignments across processes
        self.storage_path = Path("/tmp/wireless_interface_assignments.json")

        self.available_interfaces: List[str] = []

        # Load from file or initialize empty
        self._load_from_file()
        if not hasattr(self, "device_interface_map"):
            self.device_interface_map: Dict[int, str] = {}
            self.interface_device_map: Dict[str, int] = {}

        self._discover_wifi_interfaces()

        WirelessInterfaceManager._initialized = True

    def _save_to_file(self) -> None:
        """
        Save current state to file for cross-process persistence.
        """
        try:
            with global_lock("wireless_interface_manager_file_lock"):
                data = {
                    "device_interface_map": {
                        str(k): v for k, v in self.device_interface_map.items()
                    },
                    "interface_device_map": self.interface_device_map,
                }

                with open(self.storage_path, "w") as f:
                    json.dump(data, f)

        except Exception as e:
            logger.error(f"Failed to save interface assignments to file: {e}")

    def _load_from_file(self) -> None:
        """
        Load state from file.
        """
        try:
            with global_lock("wireless_interface_manager_file_lock"):
                if self.storage_path.exists():
                    with open(self.storage_path, "r") as f:
                        data = json.load(f)

                    # Convert string keys back to integers
                    self.device_interface_map = {
                        int(k): v
                        for k, v in data.get("device_interface_map", {}).items()
                    }
                    self.interface_device_map = {
                        k: int(v)
                        for k, v in data.get("interface_device_map", {}).items()
                    }

        except Exception as e:
            logger.error(f"Failed to load interface assignments from file: {e}")
            # Initialize empty if load fails
            self.device_interface_map = {}
            self.interface_device_map = {}

    def _discover_wifi_interfaces(self) -> None:
        """
        Discover all available WiFi interfaces, excluding wlan0.
        """
        try:
            cmd = ["nmcli", "device", "status"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                interfaces = []
                for line in result.stdout.strip().split("\n")[1:]:  # Skip header
                    parts = line.split()
                    if len(parts) >= 2:
                        device_name = parts[0]
                        device_type = parts[1]
                        # Include WiFi interfaces, but exclude wlan0 (hotspot)
                        if (
                            device_type == "wifi"
                            and device_name != "wlan0"
                            and device_name.startswith("wlan")
                        ):
                            interfaces.append(device_name)

                self.available_interfaces = sorted(interfaces)
                logger.info(f"Discovered WiFi interfaces: {self.available_interfaces}")
            else:
                logger.error(f"Failed to discover WiFi interfaces: {result.stderr}")
                self.available_interfaces = []

        except Exception as e:
            logger.error(f"Error discovering WiFi interfaces: {str(e)}")
            self.available_interfaces = []

    def get_available_interfaces(self) -> List[str]:
        """
        Get list of available WiFi interfaces.
        """
        return self.available_interfaces.copy()

    def assign_interface_to_device(self, device_connection_id: int) -> Optional[str]:
        """
        Assign an available WiFi interface to a device connection.

        Args:
            device_connection_id: The ID of the device connection

        Returns:
            The assigned interface name, or None if no interfaces available
        """
        # If device already has an interface assigned, return it
        if device_connection_id in self.device_interface_map:
            return self.device_interface_map[device_connection_id]

        # Find an available interface (not already assigned)
        assigned_interfaces = set(self.device_interface_map.values())
        available = [
            iface
            for iface in self.available_interfaces
            if iface not in assigned_interfaces
        ]

        if not available:
            logger.error(
                f"No available WiFi interfaces for device {device_connection_id}"
            )
            return None

        # Assign the first available interface
        interface = available[0]
        self.device_interface_map[device_connection_id] = interface
        self.interface_device_map[interface] = device_connection_id

        # Save to file immediately
        self._save_to_file()

        logger.info(
            f"Assigned interface {interface} to device connection {device_connection_id}"
        )
        return interface

    def release_interface_from_device(self, device_connection_id: int) -> bool:
        """
        Release the WiFi interface assigned to a device connection.

        Args:
            device_connection_id: The ID of the device connection

        Returns:
            True if interface was released, False if none was assigned
        """
        if device_connection_id not in self.device_interface_map:
            return False

        interface = self.device_interface_map[device_connection_id]
        del self.device_interface_map[device_connection_id]
        del self.interface_device_map[interface]

        # Save to file immediately
        self._save_to_file()

        logger.info(
            f"Released interface {interface} from device connection {device_connection_id}"
        )
        return True

    def get_device_interface(self, device_connection_id: int) -> Optional[str]:
        """
        Get the WiFi interface assigned to a device connection.

        Args:
            device_connection_id: The ID of the device connection

        Returns:
            The assigned interface name, or None if not assigned
        """
        return self.device_interface_map.get(device_connection_id)

    def connect_to_wifi(
        self, device_connection_id: int, ssid: str, password: str
    ) -> Tuple[bool, str]:
        """
        Connect to a WiFi network using nmcli on the device's assigned interface.

        Args:
            device_connection_id: The ID of the device connection
            ssid: The WiFi network SSID
            password: The WiFi network password

        Returns:
            Tuple of (success, message)
        """
        # Get or assign interface for this device
        interface = self.assign_interface_to_device(device_connection_id)
        if not interface:
            return False, "No available WiFi interfaces"

        logger.info(
            f"Attempting to connect to WiFi network '{ssid}' on interface '{interface}' for device {device_connection_id}"
        )

        try:
            cmd = [
                "nmcli",
                "device",
                "wifi",
                "connect",
                ssid,
                "password",
                password,
                "ifname",
                interface,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                logger.info(
                    f"Successfully connected to WiFi network '{ssid}' on interface '{interface}'"
                )
                return True, f"Connected to {ssid} on {interface}"
            else:
                error_msg = result.stderr.strip() or "Connection failed"
                logger.error(
                    f"Failed to connect to WiFi network '{ssid}' on interface '{interface}': {error_msg}"
                )
                return False, error_msg

        except subprocess.TimeoutExpired:
            error_msg = "Connection attempt timed out"
            logger.error(
                f"WiFi connection to '{ssid}' on interface '{interface}' timed out"
            )
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(
                f"Unexpected error connecting to WiFi '{ssid}' on interface '{interface}': {error_msg}"
            )
            return False, error_msg

    def disconnect_from_wifi(
        self, device_connection_id: int, ssid: str
    ) -> Tuple[bool, str]:
        """
        Disconnect from a WiFi network on the device's assigned interface.

        Args:
            device_connection_id: The ID of the device connection
            ssid: The WiFi network SSID to disconnect from

        Returns:
            Tuple of (success, message)
        """
        interface = self.get_device_interface(device_connection_id)
        if not interface:
            return False, "No interface assigned to this device"

        logger.info(
            f"Disconnecting from WiFi network '{ssid}' on interface '{interface}' for device {device_connection_id}"
        )

        try:
            cmd = ["nmcli", "connection", "down", ssid]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                logger.info(
                    f"Successfully disconnected from WiFi network '{ssid}' on interface '{interface}'"
                )
                self.release_interface_from_device(device_connection_id)
                return True, f"Disconnected from {ssid} on {interface}"
            else:
                error_msg = result.stderr.strip() or "Disconnection failed"
                logger.error(
                    f"Failed to disconnect from WiFi network '{ssid}' on interface '{interface}': {error_msg}"
                )
                return False, error_msg

        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(
                f"Unexpected error disconnecting from WiFi '{ssid}' on interface '{interface}': {error_msg}"
            )
            return False, error_msg

    def check_wifi_connection_status(
        self, device_connection_id: int, ssid: str
    ) -> WiFiConnectionStatus:
        """
        Check the current connection status for a device's WiFi network.

        Args:
            device_connection_id: The ID of the device connection
            ssid: The WiFi network SSID to check

        Returns:
            WiFiConnectionStatus enum value
        """
        interface = self.get_device_interface(device_connection_id)
        if not interface:
            return WiFiConnectionStatus.DISCONNECTED

        try:
            # Check if the specific interface has an active connection to this SSID
            cmd = [
                "nmcli",
                "-t",
                "-f",
                "NAME,DEVICE,STATE",
                "connection",
                "show",
                "--active",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)

            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    if not line:
                        continue
                    parts = line.split(":")
                    if len(parts) >= 3:
                        name, device, state = parts[0], parts[1], parts[2]
                        if (
                            name == ssid
                            and device == interface
                            and state == "activated"
                        ):
                            return WiFiConnectionStatus.CONNECTED

                # If we reach here, the connection is not active on this interface
                return WiFiConnectionStatus.DISCONNECTED

        except Exception as e:
            logger.error(
                f"Error checking WiFi connection status for device {device_connection_id}, SSID '{ssid}': {str(e)}"
            )
            return WiFiConnectionStatus.DISCONNECTED

    def get_current_wifi_info(
        self, device_connection_id: int
    ) -> Optional[Dict[str, str]]:
        """
        Get information about the currently connected WiFi network for a device.

        Args:
            device_connection_id: The ID of the device connection

        Returns:
            Dict with SSID and other connection info, or None if not connected
        """
        interface = self.get_device_interface(device_connection_id)
        if not interface:
            return None

        try:
            cmd = [
                "nmcli",
                "-t",
                "-f",
                "ACTIVE,SSID,SIGNAL,SECURITY",
                "device",
                "wifi",
                "list",
                "ifname",
                interface,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    if not line:
                        continue
                    parts = line.split(":", 3)
                    if len(parts) >= 2 and parts[0] == "yes":
                        return {
                            "interface": interface,
                            "ssid": parts[1],
                            "signal": parts[2] if len(parts) > 2 else "unknown",
                            "security": parts[3] if len(parts) > 3 else "unknown",
                        }

            return None

        except Exception as e:
            logger.error(
                f"Error getting current WiFi info for device {device_connection_id}: {str(e)}"
            )
            return None

    def get_interface_assignments(self) -> Dict[int, str]:
        """
        Get current device to interface assignments.

        Returns:
            Dict mapping device_connection_id to interface name
        """
        # Load from file to get latest state from other processes
        self._load_from_file()
        return self.device_interface_map.copy()

    def refresh_interfaces(self) -> None:
        """
        Re-discover available WiFi interfaces.
        This can be called to refresh the interface list if hardware changes.
        """
        logger.info("Refreshing WiFi interfaces...")
        old_interfaces = self.available_interfaces.copy()
        self._discover_wifi_interfaces()

        if self.available_interfaces != old_interfaces:
            logger.info(
                f"Interface list changed: {old_interfaces} -> {self.available_interfaces}"
            )


wireless_interface_manager = WirelessInterfaceManager()
