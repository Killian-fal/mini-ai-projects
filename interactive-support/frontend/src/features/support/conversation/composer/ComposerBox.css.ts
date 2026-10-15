import { style, styleVariants } from "@vanilla-extract/css";
import * as text from "../../../../ui/theme/text.css";
import { vars } from "../../../../ui/theme/tokens.css";

export const composer = style({ display: "flex", flexDirection: "column", gap: vars.space.x8 });

export const box = style({
  display: "flex",
  alignItems: "end",
  gap: vars.space.x16,
  padding: `${vars.space.x12} ${vars.space.x12} ${vars.space.x12} ${vars.space.x16}`,
  border: `${vars.border.width} solid`,
  borderRadius: vars.radius.card,
  transition: `background-color ${vars.motion.fast} ${vars.motion.easeOut}, border-color ${vars.motion.fast} ${vars.motion.easeOut}`,
});

export const tone = styleVariants({
  active: { borderColor: vars.color.accent, background: vars.color.surface },
  sending: { borderColor: vars.color.ink, background: vars.color.surface },
  locked: { borderColor: vars.color.mist, background: vars.color.mist },
});

export const field = style([
  text.body,
  {
    flex: 1,
    paddingBlock: vars.space.x8,
    paddingInline: 0,
    border: 0,
    background: "transparent",
    color: "inherit",
    fontFamily: "inherit",
    fieldSizing: "content",
    maxBlockSize: vars.size.composerMax,
    resize: "none",
    selectors: {
      "&:focus-visible": { outlineColor: "transparent" },
      "&:disabled": { cursor: "not-allowed" },
    },
  },
]);

export const sendingText = style({
  color: `color-mix(in oklch, ${vars.color.ink} 50%, transparent)`,
});

export const sendingButton = style({ selectors: { "&:disabled": { opacity: 0.6 } } });

export const hint = style([
  text.caption,
  { margin: 0, paddingInline: vars.space.x16, minBlockSize: "1lh" },
]);
