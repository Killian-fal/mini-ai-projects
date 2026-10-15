import { type KeyboardEvent, useEffect, useRef, useState } from "react";
import { Button } from "../../../../ui/Button";
import { cx } from "../../../../ui/cx";
import { Dots } from "../../../../ui/Dots";
import * as styles from "./ComposerBox.css";
import type { LockReason, OpenComposerState } from "./composerState";

const MAX_LENGTH = 2000;

function lockedPlaceholder(reason: LockReason): string {
  switch (reason) {
    case "card-sending":
      return "Envoi en cours…";
    case "agent-busy":
      return "Relais réfléchit…";
    case "card-pending":
      return "Répondez dans la carte ci-dessus";
  }
}

function placeholder(state: OpenComposerState): string {
  switch (state.kind) {
    case "active":
      return "Votre réponse";
    case "sending":
      return "";
    case "locked":
      return lockedPlaceholder(state.reason);
  }
}

function hint(state: OpenComposerState): string {
  switch (state.kind) {
    case "active":
      return "Entrée pour envoyer · Maj + Entrée pour aller à la ligne";
    case "sending":
      return "Envoi de votre réponse…";
    case "locked":
      return "";
  }
}

type ComposerBoxProps = {
  state: OpenComposerState;
  onSend: (text: string) => void;
};

/** @package */
export function ComposerBox({ state, onSend }: ComposerBoxProps) {
  const [draft, setDraft] = useState("");
  const field = useRef<HTMLTextAreaElement>(null);
  const actionIndex = state.kind === "active" ? state.actionIndex : null;
  const sending = state.kind === "sending";
  const text = draft.trim();
  const canSend = actionIndex !== null && text !== "";

  useEffect(() => {
    if (actionIndex !== null) {
      field.current?.focus();
    }
  }, [actionIndex]);

  function submit() {
    if (canSend) {
      onSend(text);
      setDraft("");
    }
  }

  function handleKeyDown(event: KeyboardEvent) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      submit();
    }
  }

  return (
    <div className={styles.composer}>
      <div className={cx(styles.box, styles.tone[state.kind])}>
        <textarea
          ref={field}
          rows={1}
          maxLength={MAX_LENGTH}
          aria-label="Votre réponse"
          placeholder={placeholder(state)}
          value={sending ? state.text : draft}
          disabled={actionIndex === null}
          className={cx(styles.field, sending && styles.sendingText)}
          onChange={(event) => setDraft(event.currentTarget.value)}
          onKeyDown={handleKeyDown}
        />
        <Button
          variant="primary"
          size="compact"
          disabled={!canSend}
          className={cx(sending && styles.sendingButton)}
          onClick={submit}
        >
          {sending ? (
            <>
              Envoi
              <Dots />
            </>
          ) : (
            "Envoyer"
          )}
        </Button>
      </div>
      <p className={styles.hint}>{hint(state)}</p>
    </div>
  );
}
