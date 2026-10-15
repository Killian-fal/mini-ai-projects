import { style } from "@vanilla-extract/css";
import { vars } from "../../ui/theme/tokens.css";

export const column = style({
  flex: 1,
  display: "flex",
  flexDirection: "column",
  inlineSize: "100%",
  maxInlineSize: vars.size.column,
  marginInline: "auto",
  paddingInline: vars.space.x24,
  paddingBlockEnd: vars.space.x80,
});
