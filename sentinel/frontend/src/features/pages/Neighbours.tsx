import * as stylex from "@stylexjs/stylex";
import { Link } from "react-router";
import { color, font } from "../../ui/tokens.stylex";

/** @package */
export type Neighbour = { to: string; label: string };

const styles = stylex.create({
  bar: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    gap: 16,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopStyle: "solid",
    borderTopColor: color.line,
  },
  link: {
    display: "flex",
    flexDirection: "column",
    gap: 4,
    minWidth: 0,
    maxWidth: "46%",
    textDecoration: "none",
  },
  end: { alignItems: "flex-end" },
  label: {
    fontFamily: font.data,
    fontSize: 10,
    letterSpacing: "0.08em",
    textTransform: "uppercase",
    color: color.textDim,
  },
  target: {
    fontFamily: font.data,
    fontSize: 11,
    whiteSpace: "nowrap",
    overflow: "hidden",
    textOverflow: "ellipsis",
    color: { default: color.textMuted, ":hover": color.text },
  },
});

export function Neighbours({
  previous,
  next,
}: {
  previous: Neighbour | null;
  next: Neighbour | null;
}) {
  if (previous === null && next === null) {
    return null;
  }
  return (
    <div {...stylex.props(styles.bar)}>
      {previous !== null && (
        <Link to={previous.to} {...stylex.props(styles.link)}>
          <span {...stylex.props(styles.label)}>← Page précédente</span>
          <span {...stylex.props(styles.target)}>{previous.label}</span>
        </Link>
      )}
      {next !== null && (
        <Link to={next.to} {...stylex.props(styles.link, styles.end)}>
          <span {...stylex.props(styles.label)}>Page suivante →</span>
          <span {...stylex.props(styles.target)}>{next.label}</span>
        </Link>
      )}
    </div>
  );
}
