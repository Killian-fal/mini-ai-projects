const MEGABYTE = 1024 * 1024;

/** @package */
export const MAX_MEGABYTES = 7;

/** @package */
export const ACCEPTED_TYPES = ["image/jpeg", "image/png", "image/webp"];

/** @package */
export const ACCEPTED_LABEL = "JPG, PNG ou WebP";

/** @package */
export type PhotoProblem =
  | { kind: "too-large"; name: string; bytes: number }
  | { kind: "not-an-image"; name: string };

/** @package */
export function checkPhoto(file: File): PhotoProblem | null {
  if (!ACCEPTED_TYPES.includes(file.type)) {
    return { kind: "not-an-image", name: file.name };
  }
  if (file.size > MAX_MEGABYTES * MEGABYTE) {
    return { kind: "too-large", name: file.name, bytes: file.size };
  }
  return null;
}

const megabytes = new Intl.NumberFormat("fr-FR", {
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
});

/** @package */
export function formatMegabytes(bytes: number): string {
  return `${megabytes.format(bytes / MEGABYTE)} Mo`;
}
