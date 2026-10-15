import type { ActionOf } from "../../api/conversation";
import * as styles from "./ConfirmMap.css";

const SPAN_DEGREES = 0.004;

type ConfirmMapProps = {
  location: ActionOf<"YES_NO">["location"];
};

function embedUrl(latitude: number, longitude: number): string {
  const bbox = [
    longitude - SPAN_DEGREES,
    latitude - SPAN_DEGREES,
    longitude + SPAN_DEGREES,
    latitude + SPAN_DEGREES,
  ].join(",");
  const query = new URLSearchParams({ bbox, layer: "mapnik", marker: `${latitude},${longitude}` });
  return `https://www.openstreetmap.org/export/embed.html?${query}`;
}

/** @package */
export function ConfirmMap({ location }: ConfirmMapProps) {
  if (location === null) {
    return null;
  }
  return (
    <iframe
      className={styles.map}
      title="Carte de l'adresse à confirmer"
      src={embedUrl(location.latitude, location.longitude)}
    />
  );
}
