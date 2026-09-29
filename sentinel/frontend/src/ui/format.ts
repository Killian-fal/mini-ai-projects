const FR = new Intl.NumberFormat("fr-FR");
const MB = 1_048_576;
const DAY_TIME = new Intl.DateTimeFormat("fr-FR", {
  day: "2-digit",
  month: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
});
const FULL = new Intl.DateTimeFormat("fr-FR", {
  day: "2-digit",
  month: "2-digit",
  year: "numeric",
  hour: "2-digit",
  minute: "2-digit",
});

export function count(value: number): string {
  return FR.format(value);
}

/** `1 page`, `4 218 pages`. */
export function plural(value: number, word: string): string {
  return `${count(value)} ${word}${value > 1 ? "s" : ""}`;
}

export function bytes(value: number): string {
  return value >= MB
    ? `${(value / MB).toFixed(1)} MB`
    : `${Math.round(value / 1024)} KB`;
}

export function pct(ratio: number): string {
  return `${(ratio * 100).toFixed(1)}%`;
}

export function time(iso: string): string {
  return new Date(iso).toLocaleTimeString("fr-FR", { hour12: false });
}

/** `18/09 14:02` */
export function dayTime(iso: string): string {
  return DAY_TIME.format(new Date(iso)).replace(", ", " ");
}

/** `18/09/2026 13:58` */
export function fullDate(iso: string): string {
  return FULL.format(new Date(iso)).replace(", ", " ");
}

export function midTrunc(text: string, max: number): string {
  if (text.length <= max) {
    return text;
  }
  const head = Math.ceil(max / 2) - 1;
  return `${text.slice(0, head)}…${text.slice(text.length - (max - head - 1))}`;
}

/** What follows the host in the url; empty string if the host is not in it. */
export function pathOf(url: string, host: string | null): string {
  if (host === null) {
    return "";
  }
  const start = url.indexOf(host);
  return start === -1 ? "" : url.slice(start + host.length);
}
