import { type AnswerView, answerView, hasCard } from "../../../../actions";
import type { Message } from "../../../../api/conversation";
import { type Exchange, exchanges } from "./exchanges";

export type JournalRow = {
  actionId: string;
  question: string | null;
  answer: AnswerView | null;
  targets: number[];
};

function exchangeTargets({ action, response }: Exchange): number[] {
  return [
    ...(hasCard(action.message.action) ? [action.index] : []),
    ...(response === null ? [] : [response.index]),
  ];
}

function row(group: readonly [Exchange, ...Exchange[]]): JournalRow {
  const [first] = group;
  const { action, response } = group.at(-1) ?? first;
  return {
    actionId: first.action.message.action_id,
    question: first.question?.text ?? null,
    answer:
      response === null
        ? null
        : answerView(action.message.action, response.message.response, response.message.label),
    targets: [
      ...(first.question === null ? [] : [first.question.index]),
      ...group.flatMap(exchangeTargets),
    ],
  };
}

export function journalRows(messages: readonly Message[]): JournalRow[] {
  const groups = new Map<string, [Exchange, ...Exchange[]]>();
  for (const exchange of exchanges(messages)) {
    const id = exchange.action.message.action_id;
    const group = groups.get(id);
    if (group === undefined) {
      groups.set(id, [exchange]);
    } else {
      group.push(exchange);
    }
  }
  return [...groups.values()].map(row);
}
