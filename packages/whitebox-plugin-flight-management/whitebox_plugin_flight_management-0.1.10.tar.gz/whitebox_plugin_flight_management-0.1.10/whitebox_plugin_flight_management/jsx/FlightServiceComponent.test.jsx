import { render, act } from "@testing-library/react";
import FlightServiceComponent from "./FlightServiceComponent";
import useMissionControlStore from "./stores/mission_control";

describe("FlightServiceComponent", () => {
  let messageHandler;

  beforeEach(() => {
    // Mock Whitebox.sockets
    globalThis.Whitebox.sockets = {
      addEventListener: vi.fn((channel, type, handler) => {
        if (channel === "flight" && type === "message") {
          messageHandler = handler;
        }
      }),
      removeEventListener: vi.fn(),
    };
  });

  it("should set up WebSocket event listener on mount", () => {
    render(<FlightServiceComponent />);

    expect(Whitebox.sockets.addEventListener).toHaveBeenCalledWith(
      "flight",
      "message",
      expect.any(Function)
    );
  });

  it("should update mission control store on receiving flight.start event", async () => {
    const mockSetActiveFlightSession = vi.fn();
    await act(async () => {
      await useMissionControlStore.setState({
        setActiveFlightSession: mockSetActiveFlightSession,
      })
    });

    render(<FlightServiceComponent />);

    act(() => {
      // Simulate receiving a message
      messageHandler({
        data: JSON.stringify({
          type: "flight.start",
          flight_session: {
            id: 1,
            name: "Test Flight",
          },
        }),
      });
    })

    expect(mockSetActiveFlightSession).toHaveBeenCalledWith({
      id: 1,
      name: "Test Flight",
    });
  });
});
