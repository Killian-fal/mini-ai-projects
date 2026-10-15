import { style, styleVariants } from "@vanilla-extract/css";
import { enterRow } from "../../../../ui/theme/motion.css";
import { vars } from "../../../../ui/theme/tokens.css";

export const line = style([
  enterRow,
  {
    inlineSize: `calc(100% + 2 * ${vars.space.x8})`,
    marginInline: `calc(-1 * ${vars.space.x8})`,
    padding: `${vars.space.x16} ${vars.space.x8}`,
    border: 0,
    borderBlockStart: `${vars.border.width} solid`,
    borderRadius: 0,
    background: "transparent",
    color: "inherit",
    textAlign: "start",
    cursor: "pointer",
    transition: `background-color ${vars.motion.fast} ${vars.motion.easeOut}`,
    selectors: { "&:active": { background: vars.color.mist } },
    "@media": {
      "(hover: hover) and (pointer: fine)": {
        selectors: { "&:hover": { background: vars.color.page } },
      },
    },
  },
]);

export const edge = styleVariants({
  soft: { borderBlockStartColor: vars.color.mist },
  strong: { borderBlockStartColor: vars.color.ink },
});
