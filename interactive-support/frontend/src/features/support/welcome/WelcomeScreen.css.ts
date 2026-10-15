import { style } from "@vanilla-extract/css";
import * as text from "../../../ui/theme/text.css";
import { vars } from "../../../ui/theme/tokens.css";

export const welcome = style({ gap: vars.space.x40, paddingBlockStart: vars.space.screenTop });

export const intro = style({ display: "flex", flexDirection: "column", gap: vars.space.x24 });

export const identity = style({
  margin: 0,
  display: "flex",
  alignItems: "center",
  gap: vars.space.x12,
  minBlockSize: vars.size.identity,
});

export const name = style([text.eyebrow]);

export const role = style([text.caption]);

export const title = style([text.display]);

export const lead = style([text.body, { margin: 0, maxInlineSize: vars.size.prose }]);
