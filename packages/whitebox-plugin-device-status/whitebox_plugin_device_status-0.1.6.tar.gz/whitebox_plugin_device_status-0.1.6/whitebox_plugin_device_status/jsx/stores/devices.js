import { create } from "zustand";

const createSDRDeviceSlice = (set) => ({
  sdrDeviceCount: 0,

  updateSDRStatus({ data }) {
    const numDevices = parseInt(data.Devices);
    set({ sdrDeviceCount: numDevices });
  },
});

const createGPSDeviceSlice = (set) => ({
  gpsConnected: false,
  gpsSolution: "Not communicating",
  gpsAccuracy: 0,

  updateGPSStatus({ data }) {
    const gpsConnected = data.GPS_connected === true;
    const gpsSolution = data.GPS_solution;
    const gpsAccuracy = data.GPS_position_accuracy;

    set({
      gpsConnected,
      gpsSolution,
      gpsAccuracy,
    });
  },
});

const useDevicesStore = create((...a) => ({
  ...createSDRDeviceSlice(...a),
  ...createGPSDeviceSlice(...a),
}));

export default useDevicesStore;
