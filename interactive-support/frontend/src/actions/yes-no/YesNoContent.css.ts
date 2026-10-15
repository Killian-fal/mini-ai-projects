import { style } from "@vanilla-extract/css";
import { enterOption } from "../../ui/theme/motion.css";
import { vars } from "../../ui/theme/tokens.css";

export const answers = style([
  enterOption,
  {
    display: "flex",
    flexWrap: "wrap",
    gap: vars.space.x16,
    animationDelay: vars.motion.delaySecond,
  },
]);
