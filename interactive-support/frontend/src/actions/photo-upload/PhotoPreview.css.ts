import { style } from "@vanilla-extract/css";
import { enterOption } from "../../ui/theme/motion.css";
import { vars } from "../../ui/theme/tokens.css";

export const preview = style([
  enterOption,
  {
    display: "flex",
    flexDirection: "column",
    gap: vars.space.x16,
  },
]);

export const actions = style({
  display: "flex",
  flexWrap: "wrap",
  gap: vars.space.x16,
});
