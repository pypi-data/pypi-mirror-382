import { act, screen, render, cleanup } from "@testing-library/react";
import TriggerButton from "./TriggerButton";

afterEach(cleanup);

describe("TriggerButton Component", () => {
  it("renders correctly", async () => {
    render(<TriggerButton />);

    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 0));
    });

    expect(screen.getByRole("button")).toBeInTheDocument();
    expect(screen.getByRole("button")).toHaveTextContent("Start flight");
  });
});
