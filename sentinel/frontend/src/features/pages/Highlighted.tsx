import * as stylex from "@stylexjs/stylex";
import { color, size } from "../../ui/tokens.stylex";
import { split } from "./highlight";

const styles = stylex.create({
  hit: {
    borderRadius: size.radius,
    backgroundColor: color.signal,
    color: color.bgBase,
  },
});

export function Highlighted({ text, needle }: { text: string; needle: string }) {
  return (
    <>
      {split(text, needle).map((part, index) => (
        <span
          // biome-ignore lint/suspicious/noArrayIndexKey: a fragment's only identity is its position
          key={index}
          {...stylex.props(part.hit && styles.hit)}
        >
          {part.text}
        </span>
      ))}
    </>
  );
}
