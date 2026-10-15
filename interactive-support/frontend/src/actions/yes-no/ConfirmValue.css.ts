import { style, styleVariants } from "@vanilla-extract/css";
import { enterOption } from "../../ui/theme/motion.css";
import * as text from "../../ui/theme/text.css";
import { vars } from "../../ui/theme/tokens.css";

export const value = style([
  enterOption,
  {
    margin: 0,
    padding: vars.space.x16,
    borderRadius: vars.radius.card,
    whiteSpace: "pre-wrap",
    overflowWrap: "anywhere",
    animationDelay: vars.motion.delayFirst,
    transition: `background-color ${vars.motion.base} ${vars.motion.easeOut}`,
  },
]);

export const length = styleVariants({
  short: [text.statement],
  long: [text.body],
});

export const tone = styleVariants({
  open: { background: vars.color.page },
  locked: { background: vars.color.mist },
});
