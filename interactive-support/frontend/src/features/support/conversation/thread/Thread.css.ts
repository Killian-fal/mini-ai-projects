import { style } from "@vanilla-extract/css";
import { vars } from "../../../../ui/theme/tokens.css";

export const thread = style({ display: "flex", flexDirection: "column", gap: vars.space.x24 });
