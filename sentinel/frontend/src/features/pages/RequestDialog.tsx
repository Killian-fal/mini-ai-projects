import * as stylex from "@stylexjs/stylex";
import { type ReactElement, useRef, useState } from "react";
import { usePageRequest } from "../../api/pages";
import { color, font, size } from "../../ui/tokens.stylex";

const COPIED_MS = 1400;
const TITLE_ID = "requete-jev-titre";

const styles = stylex.create({
  action: {
    fontFamily: font.data,
    fontSize: 10,
    letterSpacing: "0.08em",
    textTransform: "uppercase",
    backgroundColor: "transparent",
    borderWidth: 1,
    borderStyle: "solid",
    borderColor: { default: color.line, ":hover": color.inert },
    borderRadius: size.radius,
    padding: "3px 7px",
    cursor: { default: "pointer", ":disabled": "not-allowed" },
    color: {
      default: color.textMuted,
      ":hover": color.text,
      ":disabled": color.inert,
    },
  },
  dialog: {
    width: "min(880px, 92vw)",
    padding: 0,
    borderWidth: 1,
    borderStyle: "solid",
    borderColor: color.line,
    borderRadius: size.radius,
    backgroundColor: color.bgRaised,
    color: color.text,
  },
  head: {
    display: "flex",
    alignItems: "center",
    gap: 12,
    padding: "12px 16px",
    borderBottomWidth: 1,
    borderBottomStyle: "solid",
    borderBottomColor: color.line,
  },
  title: {
    marginTop: 0,
    marginBottom: 0,
    marginInline: 0,
    fontFamily: font.data,
    fontSize: 11,
    fontWeight: 400,
    letterSpacing: "0.09em",
    textTransform: "uppercase",
    color: color.textMuted,
  },
  spacer: { marginLeft: "auto" },
  body: { padding: "14px 16px" },
  code: {
    marginTop: 0,
    marginBottom: 0,
    marginInline: 0,
    maxHeight: "60vh",
    overflowX: "auto",
    overflowY: "auto",
    fontFamily: font.data,
    fontSize: 11.5,
    lineHeight: 1.6,
    whiteSpace: "pre-wrap",
    wordBreak: "break-word",
    color: color.textMuted,
  },
  notice: {
    fontFamily: font.data,
    fontSize: 11,
    color: color.textDim,
  },
});

export function RequestDialog({
  id,
  enabled,
}: {
  id: string;
  enabled: boolean;
}): ReactElement {
  const dialog = useRef<HTMLDialogElement>(null);
  const [open, setOpen] = useState(false);
  const [copied, setCopied] = useState(false);
  const query = usePageRequest(id, open);
  const json = query.data === undefined ? "" : JSON.stringify(query.data, null, 2);

  function show(): void {
    setOpen(true);
    dialog.current?.showModal();
  }

  function copy(): void {
    void navigator.clipboard?.writeText(json);
    setCopied(true);
    setTimeout(() => setCopied(false), COPIED_MS);
  }

  function body(): ReactElement {
    if (query.isPending) {
      return <span {...stylex.props(styles.notice)}>Chargement…</span>;
    }
    if (query.isError) {
      return (
        <span {...stylex.props(styles.notice)}>
          Aucune requête stockée pour cette détection
        </span>
      );
    }
    return <pre {...stylex.props(styles.code)}>{json}</pre>;
  }

  return (
    <>
      <button
        type="button"
        onClick={show}
        disabled={!enabled}
        {...stylex.props(styles.action)}
      >
        Requête Jev
      </button>
      <dialog
        ref={dialog}
        aria-labelledby={TITLE_ID}
        onClose={() => setOpen(false)}
        {...stylex.props(styles.dialog)}
      >
        <div {...stylex.props(styles.head)}>
          <h2 id={TITLE_ID} {...stylex.props(styles.title)}>
            Requête envoyée à Jev
          </h2>
          <span {...stylex.props(styles.spacer)} />
          <button
            type="button"
            onClick={copy}
            disabled={json === ""}
            {...stylex.props(styles.action)}
          >
            {copied ? "Copié" : "Copier"}
          </button>
          <button
            type="button"
            onClick={() => dialog.current?.close()}
            {...stylex.props(styles.action)}
          >
            Fermer
          </button>
        </div>
        <div {...stylex.props(styles.body)}>{open && body()}</div>
      </dialog>
    </>
  );
}
