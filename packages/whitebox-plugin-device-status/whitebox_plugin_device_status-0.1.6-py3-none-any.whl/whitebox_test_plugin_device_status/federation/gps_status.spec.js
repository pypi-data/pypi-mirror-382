import { expect } from "@playwright/test";
import { test } from "@tests/setup";
import { mockWhiteboxSocket, waitForWhiteboxSockets } from "@tests/helpers";

test.describe("GPS Status Component", () => {
  test.beforeEach(async ({ page }) => {
    await mockWhiteboxSocket(page, "flight");
    await page.goto("/");
    await waitForWhiteboxSockets(page, "flight");

    // Wait for the page to load so that the components that register socket
    // event handlers manage to load
    await page.waitForTimeout(1000);
  });

  test("should display disconnected GPS status initially", async ({ page }) => {
    const gpsStatusContainer = page.locator(
      '.c_device_connection:has-text("GPS")'
    );
    await expect(gpsStatusContainer).toBeVisible();
    await expect(gpsStatusContainer).toContainText("GPS");
    await expect(gpsStatusContainer).toContainText("Disconnected");
  });

  test("should update GPS status when receiving status.update message", async ({
    page,
  }) => {
    // Initial check for disconnected GPS status
    const gpsStatusContainer = page.locator(
      '.c_device_connection:has-text("GPS")'
    );
    await expect(gpsStatusContainer).toBeVisible();
    await expect(gpsStatusContainer).toContainText("GPS");
    await expect(gpsStatusContainer).toContainText("Disconnected");

    // Send GPS status update via WebSocket
    await page.evaluate(() => {
      const message = {
        type: "status.update",
        GPS_connected: true,
        GPS_solution: "3D GPS + SBAS",
        GPS_position_accuracy: 7.02282,
      };

      const event = new MessageEvent("message", {
        data: JSON.stringify(message),
      });
      const flightSocket = Whitebox.sockets.getSocket("flight", false);
      flightSocket.dispatchEvent(event);
    });

    // Check that the GPS status has been updated
    await expect(gpsStatusContainer).toContainText(
      "Connected - 3D GPS + SBAS, 7.02m"
    );
  });

  test("should show disconnected state when GPS loses connection", async ({
    page,
  }) => {
    // First, establish GPS connection
    await page.evaluate(() => {
      const message = {
        type: "status.update",
        GPS_connected: true,
        GPS_solution: "3D GPS + SBAS",
        GPS_position_accuracy: 7.02282,
      };

      const event = new MessageEvent("message", {
        data: JSON.stringify(message),
      });
      const flightSocket = Whitebox.sockets.getSocket("flight", false);
      flightSocket.dispatchEvent(event);
    });

    // Check that the GPS status is connected
    const gpsStatusContainer = page.locator(
      '.c_device_connection:has-text("GPS")'
    );
    await expect(gpsStatusContainer).toContainText(
      "Connected - 3D GPS + SBAS, 7.02m"
    );

    // Now simulate GPS disconnection
    await page.evaluate(() => {
      const message = {
        type: "status.update",
        GPS_connected: false,
        GPS_solution: "Not communicating",
        GPS_position_accuracy: 0,
      };

      const event = new MessageEvent("message", {
        data: JSON.stringify(message),
      });
      const flightSocket = Whitebox.sockets.getSocket("flight", false);
      flightSocket.dispatchEvent(event);
    });

    // Check that the GPS status has been updated to disconnected
    await expect(gpsStatusContainer).toContainText("Disconnected");
  });
});
