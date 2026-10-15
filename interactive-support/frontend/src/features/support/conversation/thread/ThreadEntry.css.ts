import { style } from "@vanilla-extract/css";
import { vars } from "../../../../ui/theme/tokens.css";

export const entry = style({
  borderRadius: vars.radius.card,
  outline: `${vars.border.focus} solid transparent`,
  outlineOffset: vars.space.x8,
  scrollMarginBlockStart: vars.space.x96,
  transition: `outline-color ${vars.motion.highlight} ${vars.motion.easeOut}`,
});

export const highlighted = style({ outlineColor: vars.color.accent });
