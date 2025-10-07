import useDevicesStore from "./devices";

describe("useDevicesStore", () => {
  beforeEach(() => {
    // Reset store to initial state before each test
    useDevicesStore.setState({
      sdrDeviceCount: 0,
      gpsConnected: false,
      gpsSolution: "Not communicating",
      gpsAccuracy: 0,
    });
  });

  describe("Initial State", () => {
    test("should have correct initial state", () => {
      const state = useDevicesStore.getState();

      expect(state.sdrDeviceCount).toBe(0);
      expect(state.gpsConnected).toBe(false);
      expect(state.gpsSolution).toBe("Not communicating");
      expect(state.gpsAccuracy).toBe(0);
    });

    test("should have all required methods", () => {
      const state = useDevicesStore.getState();

      expect(typeof state.updateSDRStatus).toBe("function");
      expect(typeof state.updateGPSStatus).toBe("function");
    });
  });

  describe("SDR Device Slice", () => {
    describe("updateSDRStatus", () => {
      test("should update SDR device count with valid number", () => {
        const { updateSDRStatus } = useDevicesStore.getState();

        updateSDRStatus({ data: { Devices: "3" } });

        const state = useDevicesStore.getState();
        expect(state.sdrDeviceCount).toBe(3);
      });

      test("should handle actual number values", () => {
        const { updateSDRStatus } = useDevicesStore.getState();

        updateSDRStatus({ data: { Devices: 7 } });

        const state = useDevicesStore.getState();
        expect(state.sdrDeviceCount).toBe(7);
      });
    });
  });

  describe("GPS Device Slice", () => {
    describe("updateGPSStatus", () => {
      test("should update GPS status with all fields", () => {
        const { updateGPSStatus } = useDevicesStore.getState();

        const gpsData = {
          GPS_connected: true,
          GPS_solution: "3D GPS + SBAS",
          GPS_position_accuracy: 7.02,
        };

        updateGPSStatus({ data: gpsData });

        const state = useDevicesStore.getState();
        expect(state.gpsConnected).toBe(true);
        expect(state.gpsSolution).toBe("3D GPS + SBAS");
        expect(state.gpsAccuracy).toBe(7.02);
      });

      test("should handle GPS disconnected state", () => {
        const { updateGPSStatus } = useDevicesStore.getState();

        const gpsData = {
          GPS_connected: false,
          GPS_solution: "No Fix",
          GPS_position_accuracy: 0,
        };

        updateGPSStatus({ data: gpsData });

        const state = useDevicesStore.getState();
        expect(state.gpsConnected).toBe(false);
        expect(state.gpsSolution).toBe("No Fix");
        expect(state.gpsAccuracy).toBe(0);
      });
    });
  });
});
