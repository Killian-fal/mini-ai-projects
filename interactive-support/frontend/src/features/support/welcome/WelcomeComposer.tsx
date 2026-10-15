import { type FormEvent, type KeyboardEvent, useState } from "react";
import { Button } from "../../../ui/Button";
import { Notice } from "../../../ui/Notice";
import * as styles from "./WelcomeComposer.css";

const MAX_LENGTH = 2000;

type WelcomeComposerProps = {
  initialDraft: string;
  failed: boolean;
  onSend: (message: string) => void;
};

/** @package */
export function WelcomeComposer({ initialDraft, failed, onSend }: WelcomeComposerProps) {
  const [draft, setDraft] = useState(initialDraft);
  const message = draft.trim();

  function submit() {
    if (message !== "") {
      onSend(message);
    }
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    submit();
  }

  function handleKeyDown(event: KeyboardEvent) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      submit();
    }
  }

  return (
    <form className={styles.composer} onSubmit={handleSubmit}>
      {failed && (
        <Notice>
          Votre message n’a pas pu être envoyé. Il est conservé ci-dessous, vous pouvez réessayer.
        </Notice>
      )}
      <div className={styles.box}>
        <textarea
          rows={5}
          maxLength={MAX_LENGTH}
          aria-label="Expliquez-nous votre problème"
          placeholder="Expliquez-nous votre problème"
          value={draft}
          className={styles.field}
          onChange={(event) => setDraft(event.currentTarget.value)}
          onKeyDown={handleKeyDown}
        />
        <div className={styles.footer}>
          <span className={styles.counter}>
            {draft.length} / {MAX_LENGTH}
            {draft.length >= MAX_LENGTH && " · limite atteinte"}
          </span>
          <Button type="submit" variant="primary" size="compact" disabled={message === ""}>
            {failed ? "Réessayer" : "Envoyer"}
          </Button>
        </div>
      </div>
    </form>
  );
}
