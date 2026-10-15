import {
  createRootRoute,
  createRoute,
  createRouter,
  Navigate,
  type RouterHistory,
} from "@tanstack/react-router";
import { SupportPage } from "../features/support";
import { RouteError } from "./RouteError";

function ToWelcome() {
  return <Navigate to="/" />;
}

const rootRoute = createRootRoute();

const supportRoute = createRoute({
  getParentRoute: () => rootRoute,
  id: "support",
  component: SupportPage,
  errorComponent: RouteError,
});

const welcomeRoute = createRoute({ getParentRoute: () => supportRoute, path: "/" });

const conversationRoute = createRoute({
  getParentRoute: () => supportRoute,
  path: "conversations/$conversationId",
});

const routeTree = rootRoute.addChildren([
  supportRoute.addChildren([welcomeRoute, conversationRoute]),
]);

export function createAppRouter(history: RouterHistory) {
  return createRouter({ routeTree, history, defaultNotFoundComponent: ToWelcome });
}

declare module "@tanstack/react-router" {
  interface Register {
    router: ReturnType<typeof createAppRouter>;
  }
}
