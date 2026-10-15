import { cleanup, configure } from "@testing-library/react";
import { afterAll, afterEach, beforeAll, beforeEach, vi } from "vitest";
import { resetConversations } from "./api/fakeApi";
import { server } from "./server";

// Testing Library advances fake timers inside waitFor only when it finds a global `jest`.
Object.assign(globalThis, {
  jest: { advanceTimersByTime: (ms: number) => vi.advanceTimersByTime(ms) },
});

Object.assign(window, { scrollTo: () => undefined });
Element.prototype.scrollIntoView = () => undefined;

configure({ asyncUtilTimeout: 10_000 });

beforeAll(() => {
  server.listen({ onUnhandledFrame: "error" });
});

beforeEach(() => {
  vi.useFakeTimers({
    toFake: ["setTimeout", "clearTimeout", "setInterval", "clearInterval", "Date"],
  });
});

afterEach(() => {
  cleanup();
  server.resetHandlers();
  resetConversations();
  vi.useRealTimers();
});

afterAll(() => {
  server.close();
});
