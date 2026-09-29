import * as stylex from "@stylexjs/stylex";
import type { ReactNode } from "react";
import { Fragment } from "react";
import { color, font } from "./tokens.stylex";

const styles = stylex.create({
  bar: {
    position: "sticky",
    top: 0,
    zIndex: 3,
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    flexWrap: "wrap",
    gap: 24,
    padding: { default: "12px 40px", "@media (max-width: 640px)": "12px 20px" },
    backgroundColor: color.bgBase,
    borderBottomWidth: 1,
    borderBottomStyle: "solid",
    borderBottomColor: color.line,
  },
  crumbs: {
    display: "flex",
    gap: 8,
    minWidth: 0,
    fontFamily: font.data,
    fontSize: 11,
    letterSpacing: "0.06em",
    color: color.textDim,
  },
  last: {
    color: color.text,
    overflow: "hidden",
    textOverflow: "ellipsis",
    whiteSpace: "nowrap",
  },
});

export function TopBar({
  crumbs,
  children,
}: {
  crumbs: ReactNode[];
  children?: ReactNode;
}) {
  return (
    <div {...stylex.props(styles.bar)}>
      <nav aria-label="Fil d'Ariane" {...stylex.props(styles.crumbs)}>
        {crumbs.map((crumb, index) => (
          // biome-ignore lint/suspicious/noArrayIndexKey: a breadcrumb is an ordered sequence
          <Fragment key={index}>
            {index > 0 && <span aria-hidden="true">/</span>}
            <span {...stylex.props(index === crumbs.length - 1 && styles.last)}>
              {crumb}
            </span>
          </Fragment>
        ))}
      </nav>
      {children}
    </div>
  );
}
