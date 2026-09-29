import * as stylex from "@stylexjs/stylex";
import type { ReactNode } from "react";
import { color } from "./tokens.stylex";

const styles = stylex.create({
  section: {
    display: "flex",
    flexDirection: "column",
    gap: 16,
    minWidth: 0,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopStyle: "solid",
    borderTopColor: color.line,
  },
  head: {
    display: "flex",
    alignItems: "baseline",
    justifyContent: "space-between",
    gap: 16,
  },
  title: { margin: 0, fontSize: 15, fontWeight: 500 },
});

export function Section({
  title,
  aside,
  children,
}: {
  title: string;
  aside?: ReactNode;
  children: ReactNode;
}) {
  return (
    <section {...stylex.props(styles.section)}>
      <div {...stylex.props(styles.head)}>
        <h2 {...stylex.props(styles.title)}>{title}</h2>
        {aside}
      </div>
      {children}
    </section>
  );
}
