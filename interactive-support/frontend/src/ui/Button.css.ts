import { style, styleVariants } from "@vanilla-extract/css";
import { motionQuery } from "./theme/motion.css";
import * as text from "./theme/text.css";
import { vars } from "./theme/tokens.css";

const inset = (space: string) => `calc(${space} - ${vars.border.width})`;

export const base = style([
  text.button,
  {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    gap: vars.space.x8,
    border: `${vars.border.width} solid transparent`,
    borderRadius: vars.radius.pill,
    color: vars.color.ink,
    cursor: "pointer",
    textAlign: "center",
    transition: `opacity ${vars.motion.base} ${vars.motion.easeOut}, background-color ${vars.motion.base} ${vars.motion.easeOut}`,
    selectors: {
      "&:disabled": { cursor: "default", opacity: 0.4, boxShadow: "none" },
      "&[aria-pressed='true']": {
        opacity: 1,
        background: vars.color.accent,
        borderColor: vars.color.ink,
        color: vars.color.ink,
      },
      "&:disabled[aria-pressed='false']": { opacity: 0.35 },
    },
    "@media": {
      [motionQuery]: {
        transition: `opacity ${vars.motion.base} ${vars.motion.easeOut}, background-color ${vars.motion.base} ${vars.motion.easeOut}, transform 160ms ${vars.motion.easeOut}`,
      },
    },
  },
]);

const hoverCream = {
  "@media": {
    "(hover: hover) and (pointer: fine)": {
      selectors: { "&:enabled:hover": { background: vars.color.page } },
    },
  },
} as const;

export const variant = styleVariants({
  primary: {
    background: vars.color.lilac,
    borderColor: vars.color.lilac,
    boxShadow: vars.shadow.press,
    selectors: {
      "&:enabled:active": { transform: "translateY(2px)", boxShadow: vars.shadow.none },
    },
  },
  outline: [
    { background: "transparent", borderColor: vars.color.ink },
    hoverCream,
    { selectors: { "&:enabled:active": { transform: "scale(0.97)" } } },
  ],
  option: [
    { background: vars.color.surface, borderColor: vars.color.ink, textAlign: "start" },
    hoverCream,
    { selectors: { "&:enabled:active": { transform: "scale(0.97)" } } },
  ],
  signal: {
    background: "transparent",
    borderColor: vars.color.signal,
    color: vars.color.signal,
    selectors: { "&:enabled:active": { transform: "scale(0.97)" } },
  },
});

export const size = styleVariants({
  large: { padding: `${inset(vars.space.x20)} ${inset(vars.space.x40)}` },
  compact: { padding: `${inset(vars.space.x12)} ${inset(vars.space.x20)}` },
  small: {
    padding: `${inset(vars.space.x8)} ${inset(vars.space.x16)}`,
    fontSize: vars.fontSize.xs,
  },
});

export const wide = style({ minWidth: vars.size.yesNo });
