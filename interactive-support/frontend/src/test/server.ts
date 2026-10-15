import { setupServer } from "msw/node";
import { handlers } from "./api/fakeApi";

export const server = setupServer(...handlers);
