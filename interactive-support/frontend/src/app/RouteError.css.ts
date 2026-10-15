import { style } from "@vanilla-extract/css";
import * as text from "../ui/theme/text.css";
import { vars } from "../ui/theme/tokens.css";

export const error = style({
  display: "flex",
  flexDirection: "column",
  alignItems: "start",
  gap: vars.space.x24,
  inlineSize: "100%",
  maxInlineSize: vars.size.column,
  marginInline: "auto",
  paddingBlock: `${vars.space.screenTopDeep} ${vars.space.x80}`,
  paddingInline: vars.space.x24,
});

export const eyebrow = style([text.eyebrow, { margin: 0 }]);

export const title = style([text.display]);

export const lead = style([text.body, { margin: 0, maxInlineSize: vars.size.prose }]);
