import { style } from "@vanilla-extract/css";
import * as text from "../../../../ui/theme/text.css";
import { vars } from "../../../../ui/theme/tokens.css";

export const end = style({
  display: "flex",
  flexDirection: "column",
  gap: vars.space.x8,
});

export const label = style([text.tag]);

export const summary = style([text.small]);
