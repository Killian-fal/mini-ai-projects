import { style } from "@vanilla-extract/css";
import { vars } from "../../ui/theme/tokens.css";

export const choices = style({
  display: "flex",
  flexWrap: "wrap",
  gap: vars.space.x8,
});
