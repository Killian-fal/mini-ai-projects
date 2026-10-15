import type { ReactNode } from "react";
import { ComposerBox } from "./ComposerBox";
import type { ComposerState } from "./composerState";
import { RestartBar } from "./RestartBar";

type ComposerProps = {
  state: ComposerState;
  onSend: (text: string) => void;
  onRestart: () => void;
};

export function Composer({ state, onSend, onRestart }: ComposerProps): ReactNode {
  switch (state.kind) {
    case "ended":
      return <RestartBar onRestart={onRestart} />;
    case "sending":
    case "locked":
    case "active":
      return <ComposerBox state={state} onSend={onSend} />;
  }
}
