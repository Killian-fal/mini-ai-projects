import { style, styleVariants } from "@vanilla-extract/css";
import * as text from "./theme/text.css";
import { vars } from "./theme/tokens.css";

export const base = style([
  text.tag,
  {
    alignSelf: "start",
    padding: `${vars.space.x4} ${vars.space.x12}`,
    border: `${vars.border.width} solid`,
    borderRadius: vars.radius.pill,
  },
]);

export const tone = styleVariants({
  waiting: { borderColor: vars.color.accent, color: vars.color.plum },
  alert: { borderColor: vars.color.ink, background: vars.color.lime },
});
