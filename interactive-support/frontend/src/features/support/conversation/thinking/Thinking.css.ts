import { style } from "@vanilla-extract/css";
import { enterMessage, fade } from "../../../../ui/theme/motion.css";
import * as text from "../../../../ui/theme/text.css";
import { vars } from "../../../../ui/theme/tokens.css";

export const thinking = style([
  enterMessage,
  {
    display: "flex",
    alignItems: "center",
    gap: vars.space.x12,
    minBlockSize: vars.space.x24,
  },
]);

export const caption = style([text.tag, fade]);
