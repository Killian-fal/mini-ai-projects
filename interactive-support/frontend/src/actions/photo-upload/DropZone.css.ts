import { style } from "@vanilla-extract/css";
import { enterOption } from "../../ui/theme/motion.css";
import * as text from "../../ui/theme/text.css";
import { vars } from "../../ui/theme/tokens.css";

export const zone = style([
  enterOption,
  {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: vars.space.x16,
    margin: 0,
    paddingBlock: vars.space.x32,
    paddingInline: vars.space.x24,
    border: `${vars.border.width} dashed ${vars.color.ink}`,
    borderRadius: vars.radius.card,
    background: vars.color.surface,
    textAlign: "center",
    animationDelay: vars.motion.delayFirst,
    transition: `background-color ${vars.motion.fast} ${vars.motion.easeOut}`,
  },
]);

export const dragging = style({ background: vars.color.page });

export const invite = style([text.body, { margin: 0 }]);

export const formats = style([text.caption, { margin: 0 }]);
