import { style } from "@vanilla-extract/css";
import * as text from "../../ui/theme/text.css";
import { vars } from "../../ui/theme/tokens.css";

export const error = style({
  display: "flex",
  flexDirection: "column",
  alignItems: "start",
  gap: vars.space.x8,
});

export const message = style([text.body, { margin: 0 }]);
