import { style } from "@vanilla-extract/css";
import * as text from "./theme/text.css";
import { vars } from "./theme/tokens.css";

export const notice = style([
  text.small,
  {
    display: "flex",
    flexWrap: "wrap",
    alignItems: "center",
    gap: vars.space.x12,
    padding: `${vars.space.x12} ${vars.space.x16}`,
    borderRadius: vars.radius.card,
    background: vars.color.mist,
  },
]);

export const icon = style([
  text.tag,
  {
    flex: "none",
    display: "grid",
    placeItems: "center",
    inlineSize: vars.size.notice,
    blockSize: vars.size.notice,
    border: `${vars.border.width} solid ${vars.color.ink}`,
    borderRadius: vars.radius.pill,
    lineHeight: 1,
  },
]);

export const message = style({ flex: "1 1 0", minInlineSize: "12rem" });
