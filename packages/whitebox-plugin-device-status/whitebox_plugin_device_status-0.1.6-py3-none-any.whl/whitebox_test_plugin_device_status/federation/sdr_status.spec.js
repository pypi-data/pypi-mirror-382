import { expect } from "@playwright/test";
import { test } from "@tests/setup";
import { mockWhiteboxSocket, waitForWhiteboxSockets } from "@tests/helpers";

test.describe("SDR Status Component", () => {
  test.beforeEach(async ({ page }) => {
    await mockWhiteboxSocket(page, "flight");
    await page.goto("/");
    await waitForWhiteboxSockets(page, "flight");

    // Wait for the page to load so that the components that register socket
    // event handlers manage to load
    await page.waitForTimeout(1000);
  });

  test("should display no SDR devices initially", async ({ page }) => {
    const sdrStatusContainer = page.locator(
      '.c_device_connection:has-text("SDR #")'
    );
    await expect(sdrStatusContainer).toHaveCount(0);
  });

  test("should display single SDR device when count is 1", async ({ page }) => {
    // Send SDR status update via WebSocket
    await page.evaluate(() => {
      const message = {
        type: "status.update",
        Devices: "1",
      };

      const event = new MessageEvent("message", {
        data: JSON.stringify(message),
      });
      const flightSocket = Whitebox.sockets.getSocket("flight", false);
      flightSocket.dispatchEvent(event);
    });

    // Check that one SDR device is displayed
    const sdrStatusContainer = page.locator(
      '.c_device_connection:has-text("SDR #1")'
    );
    await expect(sdrStatusContainer).toBeVisible();
  });

  test("should display multiple SDR devices when count is greater than 1", async ({
    page,
  }) => {
    // Send SDR status update via WebSocket
    await page.evaluate(() => {
      const message = {
        type: "status.update",
        Devices: "3",
      };

      const event = new MessageEvent("message", {
        data: JSON.stringify(message),
      });
      const flightSocket = Whitebox.sockets.getSocket("flight", false);
      flightSocket.dispatchEvent(event);
    });

    // Check that three SDR devices are displayed
    const sdrStatusContainers = page.locator(
      '.c_device_connection:has-text("SDR #")'
    );
    await expect(sdrStatusContainers).toHaveCount(3);
    await expect(sdrStatusContainers.nth(0)).toContainText("SDR #1");
    await expect(sdrStatusContainers.nth(1)).toContainText("SDR #2");
    await expect(sdrStatusContainers.nth(2)).toContainText("SDR #3");
  });

  test("should update SDR devices count when receiving status.update message", async ({
    page,
  }) => {
    // Initial check for no SDR devices
    const sdrStatusContainers = page.locator(
      '.c_device_connection:has-text("SDR #")'
    );
    await expect(sdrStatusContainers).toHaveCount(0);

    // Send SDR status update via WebSocket
    await page.evaluate(() => {
      const message = {
        type: "status.update",
        Devices: "2",
      };

      const event = new MessageEvent("message", {
        data: JSON.stringify(message),
      });
      const flightSocket = Whitebox.sockets.getSocket("flight", false);
      flightSocket.dispatchEvent(event);
    });

    // Check that two SDR devices are displayed
    await expect(sdrStatusContainers).toHaveCount(2);
    await expect(sdrStatusContainers.nth(0)).toContainText("SDR #1");
    await expect(sdrStatusContainers.nth(1)).toContainText("SDR #2");

    // Send another update to change count to 1
    await page.evaluate(() => {
      const message = {
        type: "status.update",
        Devices: "1",
      };

      const event = new MessageEvent("message", {
        data: JSON.stringify(message),
      });
      const flightSocket = Whitebox.sockets.getSocket("flight", false);
      flightSocket.dispatchEvent(event);
    });

    // Check that now only one SDR device is displayed
    await expect(sdrStatusContainers).toHaveCount(1);
    await expect(sdrStatusContainers.nth(0)).toContainText("SDR #1");
  });
});
