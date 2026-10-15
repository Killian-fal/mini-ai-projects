import { style } from "@vanilla-extract/css";
import * as text from "../../../../ui/theme/text.css";
import { vars } from "../../../../ui/theme/tokens.css";

export const agent = style({ display: "flex", flexDirection: "column", gap: vars.space.x12 });

export const signature = style([
  text.eyebrow,
  { display: "flex", alignItems: "center", gap: vars.space.x12, margin: 0 },
]);

export const body = style({
  display: "grid",
  gridTemplateColumns: `${vars.size.agentGutter} minmax(0, 1fr)`,
});

export const paragraph = style([
  text.body,
  { gridColumn: 2, margin: 0, whiteSpace: "pre-wrap", overflowWrap: "anywhere" },
]);
