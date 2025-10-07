import { useEffect } from "react";
import useDevicesStore from "./stores/devices";
const { importWhiteboxComponent } = Whitebox;

const DeviceConnection = importWhiteboxComponent(
  "device-wizard.device-connection"
);

const SDRStatus = () => {
  const sdrDeviceCount = useDevicesStore((state) => state.sdrDeviceCount);
  const updateStatus = useDevicesStore((state) => state.updateSDRStatus);

  useEffect(() => {
    return Whitebox.sockets.addEventListener("flight", "message", (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "status.update") {
        updateStatus({ data });
      }
    });
  });

  return (
    <>
      {Array.from({ length: sdrDeviceCount }, (_, index) => (
        <DeviceConnection
          key={index}
          deviceName={`SDR #${index + 1}`}
          isConnected
        />
      ))}
    </>
  );
};

export { SDRStatus };
export default SDRStatus;
