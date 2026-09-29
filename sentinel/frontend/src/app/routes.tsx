import { createBrowserRouter } from "react-router";
import { OverviewPage } from "../features/overview";
import { PageDetailPage, PagesPage } from "../features/pages";
import { RunsPage } from "../features/runs";
import { RouteError } from "./RouteError";
import { Shell } from "./Shell";

export const router = createBrowserRouter([
  {
    element: <Shell />,
    ErrorBoundary: RouteError,
    children: [
      { path: "/", element: <OverviewPage />, ErrorBoundary: RouteError },
      { path: "/pages", element: <PagesPage />, ErrorBoundary: RouteError },
      { path: "/pages/:id", element: <PageDetailPage />, ErrorBoundary: RouteError },
      { path: "/runs", element: <RunsPage />, ErrorBoundary: RouteError },
    ],
  },
]);
