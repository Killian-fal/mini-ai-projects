import { style } from "@vanilla-extract/css";
import * as text from "../../../../ui/theme/text.css";
import { vars } from "../../../../ui/theme/tokens.css";

export const recap = style({
  display: "flex",
  flexDirection: "column",
  gap: vars.space.x24,
  padding: vars.space.x24,
  borderRadius: vars.radius.card,
  background: vars.color.surface,
});

export const header = style({ display: "flex", flexDirection: "column", gap: vars.space.x8 });

export const eyebrow = style([text.eyebrow, { margin: 0 }]);

export const title = style([text.heading, { margin: 0, fontWeight: 400 }]);

export const empty = style([
  text.small,
  {
    margin: 0,
    paddingBlockStart: vars.space.x16,
    borderBlockStart: `${vars.border.width} solid ${vars.color.mist}`,
  },
]);

export const list = style({ display: "flex", flexDirection: "column", margin: 0, padding: 0 });
