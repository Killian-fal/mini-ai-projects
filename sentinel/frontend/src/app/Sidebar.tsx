import * as stylex from "@stylexjs/stylex";
import { useQuery } from "@tanstack/react-query";
import { NavLink } from "react-router";
import { overview } from "../api/overview";
import { count } from "../ui/format";
import { color, font, size } from "../ui/tokens.stylex";

const VERSION = "v0.4";

const styles = stylex.create({
  nav: {
    position: { default: "sticky", "@media (max-width: 900px)": "static" },
    top: 0,
    alignSelf: "start",
    height: { default: "100vh", "@media (max-width: 900px)": "auto" },
    display: "flex",
    flexDirection: "column",
    gap: 32,
    padding: "24px 0",
    borderRightWidth: { default: 1, "@media (max-width: 900px)": 0 },
    borderRightStyle: "solid",
    borderRightColor: color.line,
    borderBottomWidth: { default: 0, "@media (max-width: 900px)": 1 },
    borderBottomStyle: "solid",
    borderBottomColor: color.line,
  },
  brand: { display: "flex", alignItems: "baseline", gap: 8, padding: "0 20px" },
  logo: { fontSize: 15, fontWeight: 600, letterSpacing: "0.01em", color: color.text },
  version: {
    fontFamily: font.data,
    fontSize: 10,
    letterSpacing: "0.08em",
    textTransform: "uppercase",
    color: color.textDim,
  },
  group: { display: "flex", flexDirection: "column" },
  label: {
    padding: "0 20px 10px",
    fontFamily: font.data,
    fontSize: 10,
    letterSpacing: "0.09em",
    textTransform: "uppercase",
    color: color.textDim,
  },
  link: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    gap: 8,
    padding: "9px 20px",
    fontSize: 13,
    textDecoration: "none",
    borderLeftWidth: 2,
    borderLeftStyle: "solid",
    transitionDuration: size.motion,
    transitionProperty: "color, background",
    transitionTimingFunction: "ease",
    color: { default: color.textMuted, ":hover": color.text },
    backgroundColor: { default: "transparent", ":hover": color.bgRaised },
    borderLeftColor: "transparent",
  },
  active: {
    color: color.text,
    backgroundColor: color.bgRaised,
    borderLeftColor: color.signal,
  },
  count: { fontFamily: font.data, fontSize: 10, letterSpacing: "0.04em" },
  countIdle: { color: color.textDim },
  countActive: { color: color.signal },
  foot: {
    marginTop: "auto",
    display: "flex",
    flexDirection: "column",
    gap: 6,
    padding: "0 20px",
    fontFamily: font.data,
    fontSize: 10,
    letterSpacing: "0.06em",
    color: color.textDim,
  },
  service: { display: "flex", alignItems: "center", gap: 6 },
  dot: { width: 4, height: 4, borderRadius: "50%", backgroundColor: color.ok },
});

export function Sidebar() {
  const corpus = useQuery(overview.of(null));
  const flagged = corpus.data === undefined ? "—" : count(corpus.data.flagged);
  const runs = corpus.data === undefined ? "—" : count(corpus.data.runs);
  const threshold = corpus.data?.threshold;

  return (
    <nav {...stylex.props(styles.nav)}>
      <div {...stylex.props(styles.brand)}>
        <span {...stylex.props(styles.logo)}>Sentinel</span>
        <span {...stylex.props(styles.version)}>{VERSION}</span>
      </div>

      <div {...stylex.props(styles.group)}>
        <div {...stylex.props(styles.label)}>Analyse</div>
        <NavLink to="/" end {...link()}>
          Vue d'ensemble
        </NavLink>
        <NavLink to="/pages" {...link()}>
          {({ isActive }) => (
            <>
              <span>Pages</span>
              <span
                {...stylex.props(
                  styles.count,
                  isActive ? styles.countActive : styles.countIdle,
                )}
              >
                {flagged}
              </span>
            </>
          )}
        </NavLink>
        <NavLink to="/runs" {...link()}>
          {({ isActive }) => (
            <>
              <span>Runs</span>
              <span
                {...stylex.props(
                  styles.count,
                  isActive ? styles.countActive : styles.countIdle,
                )}
              >
                {runs}
              </span>
            </>
          )}
        </NavLink>
      </div>

      <div {...stylex.props(styles.foot)}>
        <div {...stylex.props(styles.service)}>
          <span {...stylex.props(styles.dot)} />
          <span>JEV · EN LIGNE</span>
        </div>
        <div>{`SEUIL ${threshold === null || threshold === undefined ? "—" : threshold.toFixed(2)}`}</div>
      </div>
    </nav>
  );
}

function link() {
  return {
    className: ({ isActive }: { isActive: boolean }) =>
      stylex.props(styles.link, isActive && styles.active).className ?? "",
  };
}
