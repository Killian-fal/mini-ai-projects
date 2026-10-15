import { style } from "@vanilla-extract/css";
import * as text from "./theme/text.css";
import { vars } from "./theme/tokens.css";

export const rule = style([
  text.tag,
  {
    display: "flex",
    alignItems: "center",
    gap: vars.space.x16,
    margin: 0,
    selectors: {
      "&::before, &::after": {
        content: "",
        flex: 1,
        blockSize: vars.border.width,
        background: vars.color.ink,
      },
    },
  },
]);
