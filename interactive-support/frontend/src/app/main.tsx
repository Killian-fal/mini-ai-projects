import "../ui/theme/global.css";
import { QueryClient } from "@tanstack/react-query";
import { createBrowserHistory } from "@tanstack/react-router";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "./App";
import { createAppRouter } from "./router";

const root = document.getElementById("root");
if (root === null) {
  throw new Error("index.html has no #root element");
}

createRoot(root).render(
  <StrictMode>
    <App router={createAppRouter(createBrowserHistory())} queryClient={new QueryClient()} />
  </StrictMode>,
);
