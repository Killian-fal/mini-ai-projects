import * as stylex from "@stylexjs/stylex";
import { Outlet } from "react-router";
import { color, font, size } from "../ui/tokens.stylex";
import { Sidebar } from "./Sidebar";

const styles = stylex.create({
  shell: {
    display: "grid",
    gridTemplateColumns: {
      default: `${size.sidebar} minmax(0, 1fr)`,
      "@media (max-width: 900px)": "minmax(0, 1fr)",
    },
    minHeight: "100vh",
    backgroundColor: color.bgBase,
    color: color.text,
    fontFamily: font.ui,
    WebkitFontSmoothing: "antialiased",
    "::selection": { backgroundColor: color.signal, color: color.bgBase },
  },
  main: { minWidth: 0 },
});

export function Shell() {
  return (
    <div {...stylex.props(styles.shell)}>
      <Sidebar />
      <main {...stylex.props(styles.main)}>
        <Outlet />
      </main>
    </div>
  );
}
