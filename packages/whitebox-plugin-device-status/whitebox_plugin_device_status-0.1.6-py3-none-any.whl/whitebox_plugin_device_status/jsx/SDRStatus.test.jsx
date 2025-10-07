import { act, render, screen, cleanup } from "@testing-library/react";
import { SDRStatus } from "./SDRStatus";

afterEach(cleanup);

describe("SDRStatus Component", () => {
  let messageHandler;

  beforeAll(() => {
    // Mock Whitebox.sockets
    window.Whitebox = {
      sockets: {
        addEventListener: vi.fn((channel, type, handler) => {
          if (channel === "flight" && type === "message") {
            messageHandler = handler;
          }
        }),
        removeEventListener: vi.fn(),
      },
    };
  });

  it("renders nothing when no SDR devices found", () => {
    render(<SDRStatus />);
    expect(screen.queryByText("SDR #1")).not.toBeInTheDocument();
  });

  it("renders SDR devices when count is greater than 0", () => {
    render(<SDRStatus />);
    expect(screen.queryByText("SDR #1")).not.toBeInTheDocument();

    act(() => {
      // Simulate receiving a message
      messageHandler({
        data: JSON.stringify({
          type: "status.update",
          Devices: "2", // Simulate 2 SDR devices
        }),
      });
    });

    expect(screen.getByText("SDR #1")).toBeInTheDocument();
    expect(screen.getByText("SDR #2")).toBeInTheDocument();
  });

  it("updates SDR device count on new messages", () => {
    render(<SDRStatus />);
    expect(screen.queryByText("SDR #1")).not.toBeInTheDocument();

    act(() => {
      // Simulate receiving a message
      messageHandler({
        data: JSON.stringify({
          type: "status.update",
          Devices: "3",
        }),
      });
    });

    expect(screen.getByText("SDR #1")).toBeInTheDocument();
    expect(screen.getByText("SDR #2")).toBeInTheDocument();
    expect(screen.getByText("SDR #3")).toBeInTheDocument();

    act(() => {
      // Simulate receiving another message with a different count
      messageHandler({
        data: JSON.stringify({
          type: "status.update",
          Devices: "1", // Simulate 1 SDR device
        }),
      });
    });

    expect(screen.getByText("SDR #1")).toBeInTheDocument();
    expect(screen.queryByText("SDR #2")).not.toBeInTheDocument();
    expect(screen.queryByText("SDR #3")).not.toBeInTheDocument();
  });
});
