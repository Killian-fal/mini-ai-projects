import * as stylex from "@stylexjs/stylex";
import { badgeOf } from "./palette";
import { font, size } from "./tokens.stylex";

const styles = stylex.create({
  badge: {
    justifySelf: "start",
    padding: "3px 7px",
    borderWidth: 1,
    borderStyle: "solid",
    borderRadius: size.radius,
    fontFamily: font.data,
    fontSize: 10,
    letterSpacing: "0.08em",
    textTransform: "uppercase",
    whiteSpace: "nowrap",
  },
});

export function Badge({ label }: { label: string }) {
  return <span {...stylex.props(styles.badge, badgeOf(label))}>{label}</span>;
}
