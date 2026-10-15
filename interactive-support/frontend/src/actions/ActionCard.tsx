import type { Action } from "../api/conversation";
import { Card } from "../ui/Card";
import type { CardProps, CardState } from "./contract";
import { moduleFor } from "./registry";

function eyebrowFor(state: CardState, prompt: string): string {
  switch (state) {
    case "pending":
      return prompt;
    case "sending":
      return "Envoi en cours";
    case "answered":
      return "Réponse envoyée";
    case "failed":
      return "Non envoyé";
  }
}

export function ActionCard(props: CardProps<Action>) {
  const { input } = moduleFor(props.action);
  if (input.kind === "composer") {
    return null;
  }
  const { prompt, width, Content } = input;
  const { state } = props.status;
  return (
    <Card tone={state} width={width} eyebrow={eyebrowFor(state, prompt)}>
      <Content {...props} />
    </Card>
  );
}
