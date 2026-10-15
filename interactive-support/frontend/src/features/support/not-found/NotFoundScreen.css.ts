import { style } from "@vanilla-extract/css";
import { enterMessage } from "../../../ui/theme/motion.css";
import * as text from "../../../ui/theme/text.css";
import { vars } from "../../../ui/theme/tokens.css";

export const notFound = style([
  enterMessage,
  { alignItems: "start", gap: vars.space.x24, paddingBlockStart: vars.space.screenTopDeep },
]);

export const eyebrow = style([text.eyebrow, { margin: 0 }]);

export const title = style([text.display]);

export const lead = style([text.body, { margin: 0, maxInlineSize: vars.size.prose }]);

export const action = style({ marginBlockStart: vars.space.x16 });
