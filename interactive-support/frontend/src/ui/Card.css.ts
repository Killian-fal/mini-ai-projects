import { style, styleVariants } from "@vanilla-extract/css";
import { enterCard } from "./theme/motion.css";
import * as text from "./theme/text.css";
import { vars } from "./theme/tokens.css";

export const card = style([
  enterCard,
  {
    inlineSize: "100%",
    display: "flex",
    flexDirection: "column",
    gap: vars.space.x16,
    padding: vars.space.x24,
    border: `${vars.border.width} solid`,
    borderRadius: vars.radius.card,
    transition: `background-color ${vars.motion.base} ${vars.motion.easeOut}, border-color ${vars.motion.base} ${vars.motion.easeOut}, opacity ${vars.motion.base} ${vars.motion.easeOut}`,
  },
]);

export const width = styleVariants({
  regular: { maxInlineSize: vars.size.card },
  narrow: { maxInlineSize: vars.size.photoCard },
});

export const tone = styleVariants({
  pending: { borderColor: vars.color.accent, background: vars.color.surface },
  sending: { borderColor: vars.color.ink, background: vars.color.surface },
  answered: { borderColor: vars.color.ink, background: "transparent" },
  failed: { borderColor: vars.color.ink, background: "transparent", opacity: 0.5 },
});

export const eyebrow = style([
  text.tag,
  { display: "flex", alignItems: "center", gap: vars.space.x8, minBlockSize: "1lh" },
]);

export const eyebrowTone = styleVariants({
  pending: { color: vars.color.plum },
  sending: { color: vars.color.ink },
  answered: { color: vars.color.ink },
  failed: { color: vars.color.ink },
});
