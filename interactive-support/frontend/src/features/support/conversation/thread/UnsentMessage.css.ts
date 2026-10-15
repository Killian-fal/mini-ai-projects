import { style } from "@vanilla-extract/css";
import * as text from "../../../../ui/theme/text.css";
import { vars } from "../../../../ui/theme/tokens.css";

export const unsent = style({ display: "flex", flexDirection: "column", gap: vars.space.x8 });

export const dimmed = style({ opacity: 0.5 });

export const label = style([text.tag, { margin: 0, textAlign: "end" }]);
