import { style } from "@vanilla-extract/css";
import * as text from "../../../../ui/theme/text.css";
import { vars } from "../../../../ui/theme/tokens.css";

export const paragraph = style([
  text.body,
  { margin: 0, whiteSpace: "pre-wrap", overflowWrap: "anywhere" },
]);

export const clamped = style({
  display: "-webkit-box",
  WebkitBoxOrient: "vertical",
  WebkitLineClamp: 8,
  overflow: "clip",
});

export const toggle = style([
  text.tag,
  {
    padding: 0,
    border: 0,
    background: "none",
    color: vars.color.plum,
    cursor: "pointer",
    textDecoration: "underline",
    textUnderlineOffset: vars.space.x4,
    selectors: { "&:active": { opacity: 0.7 } },
  },
]);
