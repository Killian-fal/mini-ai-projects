import { style } from "@vanilla-extract/css";
import * as text from "../../../ui/theme/text.css";
import { vars } from "../../../ui/theme/tokens.css";

export const composer = style({ display: "flex", flexDirection: "column", gap: vars.space.x16 });

export const box = style({
  display: "flex",
  flexDirection: "column",
  gap: vars.space.x16,
  padding: vars.space.x16,
  border: `${vars.border.width} solid ${vars.color.field}`,
  borderRadius: vars.radius.card,
  background: vars.color.surface,
  transition: `border-color ${vars.motion.fast} ${vars.motion.easeOut}`,
  selectors: { "&:focus-within": { borderColor: vars.color.accent } },
});

export const field = style([
  text.lead,
  {
    inlineSize: "100%",
    padding: 0,
    border: 0,
    background: "transparent",
    color: "inherit",
    fontFamily: "inherit",
    resize: "none",
    selectors: { "&:focus-visible": { outlineColor: "transparent" } },
  },
]);

export const footer = style({
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  gap: vars.space.x16,
});

export const counter = style([text.caption, { fontVariantNumeric: "tabular-nums" }]);
