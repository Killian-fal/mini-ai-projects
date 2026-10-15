import type { ActionOf } from "../../api/conversation";
import { Button } from "../../ui/Button";
import { type CardProps, choiceButtonProps } from "../contract";
import { ANSWERS, yesNoLabel } from "./answers";
import { ConfirmMap } from "./ConfirmMap";
import { ConfirmValue } from "./ConfirmValue";
import * as styles from "./YesNoContent.css";

/** @package */
export function YesNoContent({ action, status, onAnswer }: CardProps<ActionOf<"YES_NO">>) {
  return (
    <>
      <ConfirmValue value={action.value} locked={status.state !== "pending"} />
      <ConfirmMap location={action.location} />
      <div className={styles.answers}>
        {ANSWERS.map(({ value, variant }) => (
          <Button
            key={value}
            variant={variant}
            size="compact"
            wide={true}
            {...choiceButtonProps(status, value)}
            onClick={() => onAnswer(value)}
          >
            {yesNoLabel(value)}
          </Button>
        ))}
      </div>
    </>
  );
}
