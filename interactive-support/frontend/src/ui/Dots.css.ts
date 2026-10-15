import { style } from "@vanilla-extract/css";
import { pulse } from "./theme/motion.css";
import { vars } from "./theme/tokens.css";

export const dots = style({
  display: "inline-flex",
  alignItems: "center",
  gap: vars.space.x4,
});

export const dot = style({
  inlineSize: vars.size.dot,
  blockSize: vars.size.dot,
  borderRadius: vars.radius.pill,
  background: "currentColor",
  animation: `${pulse} 1s infinite`,
  selectors: {
    "&:nth-child(2)": { animationDelay: "0.15s" },
    "&:nth-child(3)": { animationDelay: "0.3s" },
  },
});
