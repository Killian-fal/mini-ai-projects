import { style } from "@vanilla-extract/css";
import { vars } from "../../../../ui/theme/tokens.css";

export const bar = style({
  display: "flex",
  justifyContent: "center",
  paddingBlock: `${vars.space.x8} ${vars.space.x16}`,
});
