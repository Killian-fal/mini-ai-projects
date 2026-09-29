import * as stylex from "@stylexjs/stylex";

export const screen = stylex.create({
  body: {
    display: "flex",
    flexDirection: "column",
    gap: 64,
    padding: {
      default: "44px 40px 96px",
      "@media (max-width: 640px)": "32px 20px 64px",
    },
  },
});
