import { style } from "@vanilla-extract/css";
import { vars } from "../../../../ui/theme/tokens.css";

export const row = style({ display: "flex", justifyContent: "end" });

export const bubble = style({
  maxInlineSize: "80%",
  display: "flex",
  flexDirection: "column",
  alignItems: "start",
  gap: vars.space.x8,
  padding: `${vars.space.x12} ${vars.space.x16}`,
  border: `${vars.border.width} solid ${vars.color.ink}`,
  borderRadius: vars.radius.card,
  background: vars.color.surface,
});
