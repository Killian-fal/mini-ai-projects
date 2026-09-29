import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { RouterProvider } from "react-router";
import { ApiError } from "../api/http";
import { router } from "./routes";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: (_failureCount, error) => !(error instanceof ApiError) },
  },
});

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  );
}
