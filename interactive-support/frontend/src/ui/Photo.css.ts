import { style, styleVariants } from "@vanilla-extract/css";
import { vars } from "./theme/tokens.css";

export const photo = style({
  flex: "none",
  objectFit: "cover",
  border: `${vars.border.width} solid ${vars.color.ink}`,
  background: `repeating-linear-gradient(135deg, ${vars.color.mist} 0 10px, ${vars.color.stripe} 10px 11px)`,
});

export const size = styleVariants({
  reply: { inlineSize: vars.size.photoReply, blockSize: "auto", aspectRatio: "4 / 3" },
  preview: {
    inlineSize: "100%",
    blockSize: "auto",
    aspectRatio: "4 / 3",
    maxBlockSize: vars.size.previewMax,
  },
  thumb: { inlineSize: vars.size.thumb, blockSize: "auto", aspectRatio: "4 / 3" },
  recap: { inlineSize: vars.size.recapThumb, blockSize: "auto", aspectRatio: "4 / 3" },
});
