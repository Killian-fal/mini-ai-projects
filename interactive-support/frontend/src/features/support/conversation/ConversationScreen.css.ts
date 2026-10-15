import { style } from "@vanilla-extract/css";
import { vars } from "../../../ui/theme/tokens.css";

export const layout = style({
  flex: 1,
  display: "flex",
  flexWrap: "wrap",
  gap: vars.space.x48,
  inlineSize: "100%",
  maxInlineSize: vars.size.page,
  marginInline: "auto",
  paddingInline: vars.space.x24,
});

export const aside = style({
  flex: `0 0 ${vars.size.aside}`,
  alignSelf: "start",
  position: "sticky",
  insetBlockStart: vars.space.x24,
  marginBlockStart: vars.space.x24,
  maxBlockSize: `calc(100svh - 2 * ${vars.space.x24})`,
  overflowY: "auto",
  overscrollBehavior: "contain",
});

export const main = style({
  flex: "1 1 30rem",
  maxInlineSize: vars.size.column,
  display: "flex",
  flexDirection: "column",
});

export const flow = style({
  flex: 1,
  display: "flex",
  flexDirection: "column",
  gap: vars.space.x24,
  paddingBlock: `${vars.space.x24} ${vars.space.x40}`,
});

export const composer = style({
  position: "sticky",
  insetBlockEnd: 0,
  paddingBlock: `${vars.space.x16} ${vars.space.x24}`,
  background: vars.color.page,
});
