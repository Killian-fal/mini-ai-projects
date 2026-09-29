import * as stylex from "@stylexjs/stylex";
import type { ReactElement } from "react";
import { isRouteErrorResponse, Link, useRouteError } from "react-router";
import { Notice } from "../ui/Notice";
import { screen } from "../ui/screen";
import { TopBar } from "../ui/TopBar";
import { color, font, size } from "../ui/tokens.stylex";

const styles = stylex.create({
  link: {
    fontFamily: font.data,
    fontSize: 10,
    letterSpacing: "0.09em",
    textTransform: "uppercase",
    textDecoration: "none",
    borderRadius: size.radius,
    color: { default: color.textMuted, ":hover": color.text },
  },
});

function message(error: unknown): { message: string; detail: string } {
  if (isRouteErrorResponse(error) && error.status === 404) {
    return { message: "Cette page n'existe pas", detail: "Lien incomplet ou périmé" };
  }
  return {
    message: "Cet écran n'a pas pu s'afficher",
    detail: error instanceof Error ? error.message : "Aucun détail disponible",
  };
}

export function RouteError(): ReactElement {
  return (
    <>
      <TopBar crumbs={["SENTINEL", "ERREUR"]}>
        <Link to="/" {...stylex.props(styles.link)}>
          Vue d'ensemble →
        </Link>
      </TopBar>
      <div {...stylex.props(screen.body)}>
        <Notice {...message(useRouteError())} />
      </div>
    </>
  );
}
