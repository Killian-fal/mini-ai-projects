import * as stylex from "@stylexjs/stylex";
import { color, font, size } from "./tokens.stylex";

const styles = stylex.create({
  block: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: 10,
    padding: "56px 24px",
    backgroundColor: color.bgSurface,
    borderWidth: 1,
    borderStyle: "solid",
    borderColor: color.line,
    borderRadius: size.radius,
  },
  message: { fontSize: 15, color: color.text, textAlign: "center" },
  detail: {
    fontFamily: font.data,
    fontSize: 10,
    letterSpacing: "0.08em",
    textTransform: "uppercase",
    color: color.textDim,
    textAlign: "center",
  },
});

export function Notice({ message, detail }: { message: string; detail?: string }) {
  return (
    <div {...stylex.props(styles.block)}>
      <span {...stylex.props(styles.message)}>{message}</span>
      {detail !== undefined && <span {...stylex.props(styles.detail)}>{detail}</span>}
    </div>
  );
}
