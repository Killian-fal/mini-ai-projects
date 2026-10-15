import { style } from "@vanilla-extract/css";
import * as text from "../../../../ui/theme/text.css";
import { vars } from "../../../../ui/theme/tokens.css";

export const row = style({
  display: "grid",
  gridTemplateColumns: `${vars.size.recapIndex} minmax(0, 1fr)`,
  gap: vars.space.x8,
});

export const number = style([text.tag, { fontVariantNumeric: "tabular-nums" }]);

export const detail = style({
  display: "flex",
  flexDirection: "column",
  alignItems: "start",
  gap: vars.space.x8,
});

export const question = style([text.tag]);

export const answer = style([text.answer, { overflowWrap: "anywhere" }]);
