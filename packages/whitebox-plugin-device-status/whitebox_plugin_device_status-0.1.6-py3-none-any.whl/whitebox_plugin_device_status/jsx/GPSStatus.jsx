import { useEffect } from "react";
import useDevicesStore from "./stores/devices";
const { importWhiteboxComponent } = Whitebox;

const DeviceConnection = importWhiteboxComponent(
  "device-wizard.device-connection"
);

const GPSStatus = () => {
  const gpsConnected = useDevicesStore((state) => state.gpsConnected);
  const gpsSolution = useDevicesStore((state) => state.gpsSolution);
  const gpsAccuracy = useDevicesStore((state) => state.gpsAccuracy);
  const updateGPSStatus = useDevicesStore((state) => state.updateGPSStatus);

  useEffect(() => {
    return Whitebox.sockets.addEventListener("flight", "message", (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "status.update") {
        updateGPSStatus({ data });
      }
    });
  }, []);

  const getConnectionInfo = () => {
    if (!gpsConnected)
      return null;

    // Stratux-specific, to be standardized in #178
    if (gpsSolution === "No Fix")
      return "Acquiring satellite fix...";

    return `${gpsSolution}, ${gpsAccuracy.toFixed(2)}m`;
  };

  return (
    <DeviceConnection deviceName="GPS"
                      isConnected={gpsConnected}
                      connectionInfo={getConnectionInfo()} />
  );
};

export { GPSStatus };
export default GPSStatus;
