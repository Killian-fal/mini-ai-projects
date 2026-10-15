import type { ReactNode } from "react";
import * as styles from "./Card.css";
import { cx } from "./cx";
import { Dots } from "./Dots";

type CardTone = keyof typeof styles.tone;

type CardProps = {
  tone: CardTone;
  width: keyof typeof styles.width;
  eyebrow: string;
  children: ReactNode;
};

export function Card({ tone, width, eyebrow, children }: CardProps) {
  return (
    <section className={cx(styles.card, styles.width[width], styles.tone[tone])}>
      <p className={cx(styles.eyebrow, styles.eyebrowTone[tone])}>
        {eyebrow}
        {tone === "sending" && <Dots />}
      </p>
      {children}
    </section>
  );
}
