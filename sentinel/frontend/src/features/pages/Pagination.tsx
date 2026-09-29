import * as stylex from "@stylexjs/stylex";
import { count } from "../../ui/format";
import { color, font, size } from "../../ui/tokens.stylex";

const styles = stylex.create({
  bar: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    gap: 16,
  },
  range: {
    fontFamily: font.data,
    fontSize: 10,
    letterSpacing: "0.08em",
    textTransform: "uppercase",
    color: color.textDim,
  },
  buttons: { display: "flex", alignItems: "center", gap: 8 },
  button: {
    fontFamily: font.data,
    fontSize: 10,
    letterSpacing: "0.08em",
    textTransform: "uppercase",
    backgroundColor: "transparent",
    borderWidth: 1,
    borderStyle: "solid",
    borderColor: { default: color.line, ":hover": color.inert },
    borderRadius: size.radius,
    padding: "5px 10px",
    cursor: "pointer",
    color: { default: color.textMuted, ":hover": color.text },
  },
  page: { fontFamily: font.data, fontSize: 11, color: color.text },
});

export function Pagination({
  page,
  perPage,
  total,
  onPage,
}: {
  page: number;
  perPage: number;
  total: number;
  onPage: (page: number) => void;
}) {
  const last = Math.max(1, Math.ceil(total / perPage));
  const first = (page - 1) * perPage + 1;

  return (
    <div {...stylex.props(styles.bar)}>
      <span {...stylex.props(styles.range)}>
        {total === 0
          ? "0 résultat"
          : `${first}–${Math.min(total, first + perPage - 1)} sur ${count(total)}`}
      </span>
      <div {...stylex.props(styles.buttons)}>
        <button
          type="button"
          onClick={() => onPage(Math.max(1, page - 1))}
          {...stylex.props(styles.button)}
        >
          ← Préc.
        </button>
        <span {...stylex.props(styles.page)}>{`${page} / ${last}`}</span>
        <button
          type="button"
          onClick={() => onPage(Math.min(last, page + 1))}
          {...stylex.props(styles.button)}
        >
          Suiv. →
        </button>
      </div>
    </div>
  );
}
