import type { FormEvent } from "react";
import type { ActionOf } from "../../api/conversation";
import { Button } from "../../ui/Button";
import type { CardProps } from "../contract";
import * as styles from "./FormContent.css";
import { sentValues } from "./sentValues";

/** @package */
export function FormContent({ action, status, onAnswer }: CardProps<ActionOf<"FORM">>) {
  const pending = status.state === "pending";
  const sent = pending ? null : sentValues(status.response);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onAnswer(JSON.stringify(Object.fromEntries(new FormData(event.currentTarget))));
  }

  return (
    <form className={styles.form} onSubmit={handleSubmit}>
      <fieldset disabled={!pending} className={styles.fields}>
        {action.fields.map((field) => (
          <label key={field.key} className={styles.field}>
            <span className={styles.label}>{field.label}</span>
            <input
              name={field.key}
              defaultValue={sent?.[field.key] ?? field.value}
              required={true}
              className={styles.input}
            />
          </label>
        ))}
      </fieldset>
      {pending && (
        <Button type="submit" variant="primary" size="compact" className={styles.submit}>
          Valider
        </Button>
      )}
    </form>
  );
}
