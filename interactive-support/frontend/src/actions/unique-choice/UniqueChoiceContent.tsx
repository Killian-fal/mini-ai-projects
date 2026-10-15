import type { ActionOf } from "../../api/conversation";
import { Button } from "../../ui/Button";
import { enterOption } from "../../ui/theme/motion.css";
import { vars } from "../../ui/theme/tokens.css";
import { type CardProps, choiceButtonProps } from "../contract";
import * as styles from "./UniqueChoiceContent.css";

/** @package */
export function UniqueChoiceContent({
  action,
  status,
  onAnswer,
}: CardProps<ActionOf<"UNIQUE_CHOICE">>) {
  return (
    <div className={styles.choices}>
      {action.choices.map((choice, index) => (
        <Button
          key={choice.key}
          variant="option"
          size="compact"
          className={enterOption}
          style={{
            animationDelay: `calc(${vars.motion.delayFirst} + ${index} * ${vars.motion.delayStep})`,
          }}
          {...choiceButtonProps(status, choice.key)}
          onClick={() => onAnswer(choice.key)}
        >
          {choice.label}
        </Button>
      ))}
    </div>
  );
}
