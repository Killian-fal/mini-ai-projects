import { style } from "@vanilla-extract/css";
import { enterOption } from "../../ui/theme/motion.css";
import { vars } from "../../ui/theme/tokens.css";

export const map = style([
  enterOption,
  {
    display: "block",
    inlineSize: "100%",
    blockSize: "auto",
    aspectRatio: "16 / 9",
    border: `${vars.border.width} solid ${vars.color.ink}`,
    borderRadius: vars.radius.card,
    background: vars.color.mist,
    animationDelay: vars.motion.delayFirst,
  },
]);
