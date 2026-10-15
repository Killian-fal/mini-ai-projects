import { style } from "@vanilla-extract/css";
import { vars } from "./tokens.css";

const label = {
  fontFamily: vars.font.label,
  fontWeight: 700,
  textTransform: "uppercase",
} as const;

export const display = style({
  margin: 0,
  fontWeight: 400,
  fontSize: vars.fontSize.display,
  lineHeight: 1,
  letterSpacing: "-0.7px",
});

export const title = style({
  fontSize: vars.fontSize.xl,
  lineHeight: 1.13,
  letterSpacing: "-1px",
});

export const heading = style({
  fontSize: vars.fontSize.lg,
  lineHeight: 1.09,
  letterSpacing: "-0.9px",
});

export const lead = style({
  fontSize: vars.fontSize.lg,
  lineHeight: 1.4,
  letterSpacing: "-0.8px",
});

export const statement = style({
  fontSize: vars.fontSize.lg,
  lineHeight: 1.2,
  letterSpacing: "-0.9px",
});

export const body = style({
  fontSize: vars.fontSize.md,
  lineHeight: 1.5,
  letterSpacing: "-0.4px",
});

export const answer = style({
  fontSize: vars.fontSize.md,
  lineHeight: 1.4,
  letterSpacing: "-0.5px",
});

export const small = style({
  fontSize: vars.fontSize.sm,
  lineHeight: 1.5,
  letterSpacing: "-0.3px",
});

export const caption = style({
  fontSize: vars.fontSize.xs,
  lineHeight: 1.5,
  letterSpacing: "-0.3px",
});

export const eyebrow = style({
  ...label,
  fontSize: vars.fontSize.sm,
  lineHeight: 1.43,
  letterSpacing: "0.063em",
});

export const tag = style({
  ...label,
  fontSize: vars.fontSize.xs,
  lineHeight: 1.5,
  letterSpacing: "0.05em",
});

export const button = style({
  ...label,
  fontSize: vars.fontSize.sm,
  lineHeight: 1.2,
  letterSpacing: "0.05em",
});
