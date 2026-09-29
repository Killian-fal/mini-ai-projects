import stylex from "@stylexjs/unplugin";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

export default defineConfig(({ mode }) => {
  const stylexPlugin = stylex.vite({});
  return {
    plugins: [
      react(),
      // L'intervalle HMR de StyleX n'est arrêté que par la fermeture d'un serveur
      // HTTP, que Vitest n'ouvre jamais : le process de test ne rendrait pas la main.
      mode === "test" ? { ...stylexPlugin, configureServer: undefined } : stylexPlugin,
    ],
    test: { environment: "jsdom", setupFiles: ["./src/test-setup.ts"] },
  };
});
