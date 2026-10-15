function isTextRecord(value: unknown): value is Record<string, string> {
  return (
    typeof value === "object" &&
    value !== null &&
    !Array.isArray(value) &&
    Object.values(value).every((field) => typeof field === "string")
  );
}

/** @package */
export function sentValues(response: string): Record<string, string> | null {
  // An answer the server rejected is stored as sent: it may not be a form at all.
  try {
    const sent: unknown = JSON.parse(response);
    return isTextRecord(sent) ? sent : null;
  } catch {
    return null;
  }
}
