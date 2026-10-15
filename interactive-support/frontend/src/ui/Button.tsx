import type { ComponentPropsWithRef } from "react";
import * as styles from "./Button.css";
import { cx } from "./cx";

type ButtonProps = ComponentPropsWithRef<"button"> & {
  variant: keyof typeof styles.variant;
  size: keyof typeof styles.size;
  wide?: boolean;
};

export function Button({ variant, size, wide = false, className, type, ...props }: ButtonProps) {
  return (
    <button
      type={type ?? "button"}
      className={cx(
        styles.base,
        styles.variant[variant],
        styles.size[size],
        wide && styles.wide,
        className,
      )}
      {...props}
    />
  );
}
