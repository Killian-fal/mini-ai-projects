import { createVar, keyframes, style, styleVariants } from "@vanilla-extract/css";
import { motionQuery } from "./theme/motion.css";
import { vars } from "./theme/tokens.css";

const disc = createVar();
const shift = "12px";

const towardsEnd = keyframes({ "50%": { transform: `translateX(${shift})` } });
const towardsStart = keyframes({ "50%": { transform: `translateX(-${shift})` } });

export const mark = style({
  display: "grid",
  flex: "none",
  inlineSize: `calc(${disc} + ${shift})`,
  blockSize: disc,
});

export const size = styleVariants({
  small: { vars: { [disc]: "16px" } },
  large: { vars: { [disc]: "20px" } },
});

const circle = style({
  gridArea: "1 / 1",
  inlineSize: disc,
  blockSize: disc,
  border: `${vars.border.width} solid ${vars.color.ink}`,
  borderRadius: vars.radius.pill,
});

export const agent = style([circle, { background: vars.color.accent, zIndex: 1 }]);
export const team = style([circle, { background: vars.color.surface, marginInlineStart: shift }]);

const swap = (name: string) => ({
  "@media": {
    [motionQuery]: {
      animation: `${name} 1.6s ${vars.motion.swapEase} infinite`,
    },
  },
});

export const agentSwapping = style(swap(towardsEnd));
export const teamSwapping = style(swap(towardsStart));
