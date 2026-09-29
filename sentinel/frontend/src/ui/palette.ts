import type { StyleXStyles } from "@stylexjs/stylex";
import * as stylex from "@stylexjs/stylex";
import { bucketColor, channelColor, color } from "./tokens.stylex";

export const CHANNELS = [
  "visible",
  "hidden",
  "comment",
  "header",
  "meta",
  "attr",
  "script",
];

export const KEY_CHANNELS = ["hidden", "comment", "header"];

const badges = stylex.create({
  hiring: {
    color: bucketColor.hiringText,
    borderColor: bucketColor.hiringLine,
    backgroundColor: bucketColor.hiringBg,
  },
  reputation: {
    color: bucketColor.reputationText,
    borderColor: bucketColor.reputationLine,
    backgroundColor: bucketColor.reputationBg,
  },
  academic: {
    color: bucketColor.academicText,
    borderColor: bucketColor.academicLine,
    backgroundColor: bucketColor.academicBg,
  },
  support: {
    color: bucketColor.supportText,
    borderColor: bucketColor.supportLine,
    backgroundColor: bucketColor.supportBg,
  },
  cheap_tld: {
    color: bucketColor.cheapTldText,
    borderColor: bucketColor.cheapTldLine,
    backgroundColor: bucketColor.cheapTldBg,
  },
  control: {
    color: bucketColor.controlText,
    borderColor: bucketColor.controlLine,
    backgroundColor: bucketColor.controlBg,
  },
  other: {
    color: bucketColor.otherText,
    borderColor: bucketColor.otherLine,
    backgroundColor: bucketColor.otherBg,
  },
});

/** Categories come from the database: an unknown one gets this neutral hue. */
const unknown = stylex.create({
  bucket: {
    color: color.textDim,
    borderColor: color.line,
    backgroundColor: color.bgSurface,
  },
});

const chips = stylex.create({
  visible: { color: channelColor.visible },
  hidden: { color: channelColor.hidden },
  comment: { color: channelColor.comment },
  header: { color: channelColor.header },
  meta: { color: channelColor.meta },
  attr: { color: channelColor.attr },
  script: { color: channelColor.script },
});

const byBucket: Record<string, StyleXStyles> = badges;
const byChannel: Record<string, StyleXStyles> = chips;

export function badgeOf(bucket: string): StyleXStyles {
  return byBucket[bucket] ?? unknown.bucket;
}

export function chipOf(channel: string): StyleXStyles {
  return byChannel[channel] ?? chips.visible;
}
