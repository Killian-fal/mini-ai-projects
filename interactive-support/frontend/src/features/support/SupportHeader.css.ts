import { style } from "@vanilla-extract/css";
import * as text from "../../ui/theme/text.css";
import { vars } from "../../ui/theme/tokens.css";

export const header = style({
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  gap: vars.space.x24,
  inlineSize: "100%",
  maxInlineSize: vars.size.page,
  marginInline: "auto",
  padding: vars.space.x24,
});

export const brand = style({
  margin: 0,
  display: "flex",
  alignItems: "baseline",
  gap: vars.space.x16,
});

export const shop = style([text.title]);

export const section = style([text.eyebrow]);

export const customer = style({
  margin: 0,
  display: "flex",
  alignItems: "center",
  gap: vars.space.x16,
});

export const name = style([text.answer]);

export const avatar = style([
  text.tag,
  {
    display: "grid",
    placeItems: "center",
    inlineSize: vars.size.avatar,
    blockSize: vars.size.avatar,
    border: `${vars.border.width} solid ${vars.color.ink}`,
    borderRadius: vars.radius.pill,
    background: vars.color.lilac,
  },
]);
