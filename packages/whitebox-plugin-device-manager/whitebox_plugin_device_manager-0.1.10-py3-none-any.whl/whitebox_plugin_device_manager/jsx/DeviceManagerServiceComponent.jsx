import { useEffect } from "react";
import useDevicesStore from "./stores/devices";

const DeviceManagerServiceComponent = () => {
  // Immediately on page load, fetch device list and populate the state store
  // with it, so that it's immediately available anywhere it's needed

  const fetchDevices = useDevicesStore((state) => state.fetchDevices);

  useEffect(() => {
    fetchDevices();
  }, []);

  return null;
}

export { DeviceManagerServiceComponent };
export default DeviceManagerServiceComponent;
