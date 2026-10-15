import { QueryClient } from "@tanstack/react-query";
import { createMemoryHistory } from "@tanstack/react-router";
import { render } from "@testing-library/react";
import { userEvent } from "@testing-library/user-event";
import { vi } from "vitest";
import { App } from "../app/App";
import { createAppRouter } from "../app/router";

export function renderApp(url = "/") {
  const router = createAppRouter(createMemoryHistory({ initialEntries: [url] }));
  const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime, applyAccept: false });
  render(<App router={router} queryClient={new QueryClient()} />);
  return { user, router };
}
