import { style } from "@vanilla-extract/css";
import { enterOption } from "../../ui/theme/motion.css";
import * as text from "../../ui/theme/text.css";
import { vars } from "../../ui/theme/tokens.css";

export const form = style({
  display: "flex",
  flexDirection: "column",
  alignItems: "start",
  gap: vars.space.x16,
});

export const fields = style([
  enterOption,
  {
    alignSelf: "stretch",
    display: "flex",
    flexDirection: "column",
    gap: vars.space.x12,
    margin: 0,
    padding: 0,
    border: 0,
    animationDelay: vars.motion.delayFirst,
  },
]);

export const field = style({ display: "flex", flexDirection: "column", gap: vars.space.x4 });

export const label = style([text.small]);

export const input = style([
  text.body,
  {
    paddingBlock: vars.space.x8,
    paddingInline: vars.space.x12,
    border: `${vars.border.width} solid ${vars.color.stripe}`,
    borderRadius: vars.radius.card,
    background: vars.color.page,
    color: vars.color.ink,
    fontFamily: "inherit",
    transition: `background-color ${vars.motion.base} ${vars.motion.easeOut}`,
    selectors: {
      "&:disabled": {
        borderColor: vars.color.mist,
        background: vars.color.mist,
        opacity: 1,
        WebkitTextFillColor: "currentColor",
      },
    },
  },
]);

export const submit = style([enterOption, { animationDelay: vars.motion.delaySecond }]);
