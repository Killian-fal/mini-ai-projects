import * as stylex from "@stylexjs/stylex";

export const color = stylex.defineVars({
  bgBase: "var(--sentinel-bg-base)",
  bgSurface: "#0f1216",
  bgRaised: "#12151b",
  bgSignalRow: "#101216",
  bgRowHover: "#15181e",
  bgRowHoverSignal: "#14171d",
  bgChannelKey: "#141311",
  line: "#232830",
  lineSoft: "#1a1e25",
  text: "var(--sentinel-text)",
  textStrong: "#ffffff",
  textMuted: "#8b929e",
  textDim: "#5f6673",
  signal: "var(--sentinel-signal)",
  signalHover: "#ff8142",
  ok: "#5d9c6e",
  inert: "#3a4150",
  inertSoft: "#4a5260",
  errorText: "#a8b0bd",
  barNeutral: "#2c3340",
  gauge: "linear-gradient(90deg, #0d6ea5, #2f7f93, #9a8a3c, #fb631b)",
});

export const bucketColor = stylex.defineVars({
  hiringText: "#c79a72",
  hiringLine: "#4a3a2c",
  hiringBg: "#171310",
  reputationText: "#a2a0bd",
  reputationLine: "#343349",
  reputationBg: "#131318",
  academicText: "#8fb0bd",
  academicLine: "#2b3d45",
  academicBg: "#101417",
  supportText: "#8b929e",
  supportLine: "#2c3340",
  supportBg: "#12151b",
  cheapTldText: "#bd9a9a",
  cheapTldLine: "#452e2e",
  cheapTldBg: "#171112",
  controlText: "#5f6673",
  controlLine: "#232830",
  controlBg: "#0f1216",
  otherText: "#8aa38f",
  otherLine: "#2e3d33",
  otherBg: "#101410",
});

export const jsonColor = stylex.defineVars({
  key: "#8fb0bd",
  string: "#c8cdd6",
  number: "#d8a13a",
  literal: "#7f8a7a",
  punctuation: "#4a5260",
});

export const channelColor = stylex.defineVars({
  visible: "#7c8596",
  hidden: "#d8a13a",
  header: "#b06fa0",
  comment: "#4a9ec9",
  meta: "#7f8a7a",
  attr: "#8a7f95",
  script: "#98846b",
});

export const font = stylex.defineVars({
  ui: "var(--sentinel-font-ui)",
  data: "'IBM Plex Mono', ui-monospace, monospace",
});

export const size = stylex.defineVars({
  sidebar: "208px",
  radius: "2px",
  radiusTight: "1px",
  motion: "var(--sentinel-motion)",
  pagesGrid: "3px minmax(0, 1fr) 96px 132px 92px",
  listGrid: "3px minmax(240px, 1fr) 96px 132px 96px 74px 92px",
  runsGrid: "3px 104px 110px 54px 82px 82px 70px 96px 74px 92px 84px",
  aside: "340px",
  asideTop: "45px",
});
