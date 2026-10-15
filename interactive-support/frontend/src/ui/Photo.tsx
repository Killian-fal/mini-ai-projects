import { cx } from "./cx";
import * as styles from "./Photo.css";

type PhotoProps = {
  src: string;
  alt: string;
  size: keyof typeof styles.size;
  className?: string;
};

export function Photo({ src, alt, size, className }: PhotoProps) {
  return <img src={src} alt={alt} className={cx(styles.photo, styles.size[size], className)} />;
}
