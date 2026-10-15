import { globalStyle } from "@vanilla-extract/css";
import { vars } from "./tokens.css";

globalStyle("*, *::before, *::after", {
  boxSizing: "border-box",
  minWidth: 0,
});

globalStyle(":root", {
  interpolateSize: "allow-keywords",
  scrollbarGutter: "stable",
  textWrap: "pretty",
  overflowWrap: "break-word",
  fontSynthesis: "none",
  WebkitFontSmoothing: "antialiased",
  MozOsxFontSmoothing: "grayscale",
  WebkitTextSizeAdjust: "100%",
  WebkitTapHighlightColor: "transparent",
  overscrollBehaviorY: "none",
  "@media": {
    "(prefers-reduced-motion: no-preference)": { scrollBehavior: "smooth" },
  },
});

globalStyle("body", {
  margin: 0,
  minHeight: "100svh",
  background: vars.color.page,
  color: vars.color.ink,
  fontFamily: vars.font.body,
  fontSize: vars.fontSize.md,
  lineHeight: 1.5,
  letterSpacing: "-0.4px",
});

globalStyle("h1, h2, h3, h4", { textWrap: "balance" });

globalStyle("img, svg, video", {
  display: "block",
  maxWidth: "100%",
  height: "auto",
});

globalStyle("input, textarea, select", { fontSize: "max(16px, 1rem)" });

globalStyle("button, a, [role='button']", { touchAction: "manipulation" });

globalStyle("button, [role='button']", {
  userSelect: "none",
  WebkitUserSelect: "none",
});

globalStyle("::placeholder", { color: vars.color.placeholder, opacity: 1 });

globalStyle(":focus-visible", {
  outline: `${vars.border.focus} solid ${vars.color.accent}`,
  outlineOffset: vars.space.x2,
});
