import { useNavigate, useParams } from "@tanstack/react-router";
import {
  type AnswerVariables,
  type Language,
  type Message,
  useAnswer,
  useConversation,
  useStartConversation,
} from "../../api/conversation";
import type { SentAnswer } from "./conversation/model";

type ConversationView = {
  messages: readonly Message[];
  language: Language | null;
  waiting: boolean;
  outgoing: SentAnswer | null;
  failure: SentAnswer | null;
};

/** @package */
export type SupportQuery =
  | { screen: "welcome"; draft: string; failed: boolean; send: (message: string) => void }
  | {
      screen: "conversation";
      view: ConversationView;
      answer: (answer: SentAnswer) => void;
      restart: () => void;
    }
  | { screen: "not-found"; restart: () => void }
  | { screen: "loading" };

type Delivery = Pick<ConversationView, "outgoing" | "failure">;

function sent({ actionId, response }: AnswerVariables): SentAnswer {
  return { actionId, response };
}

function deliveryOf(answer: ReturnType<typeof useAnswer>, conversationId: string): Delivery {
  const { variables } = answer;
  if (variables?.conversationId !== conversationId) {
    return { outgoing: null, failure: null };
  }
  return {
    outgoing: answer.isPending ? sent(variables) : null,
    failure: answer.isError ? sent(variables) : null,
  };
}

function openingQuery(
  start: ReturnType<typeof useStartConversation>,
  send: (message: string) => void,
  respond: (conversationId: string | undefined) => (answer: SentAnswer) => void,
  restart: () => void,
): SupportQuery {
  const message = start.variables ?? "";
  if (start.isIdle || start.isError) {
    return { screen: "welcome", draft: message, failed: start.isError, send };
  }
  const created = start.data;
  return {
    screen: "conversation",
    view: {
      messages: created?.messages ?? [{ role: "USER", text: message }],
      language: created?.language ?? null,
      waiting: start.isPending,
      outgoing: null,
      failure: null,
    },
    answer: respond(created?.id),
    restart,
  };
}

/** @package */
export function useSupport(): SupportQuery {
  const { conversationId } = useParams({ strict: false });
  const navigate = useNavigate();
  const conversation = useConversation(conversationId);
  const start = useStartConversation();
  const answer = useAnswer();

  function restart() {
    start.reset();
    answer.reset();
    void navigate({ to: "/" });
  }

  function send(message: string) {
    start.mutate(message, {
      onSuccess: ({ id }) =>
        navigate({ to: "/conversations/$conversationId", params: { conversationId: id } }).then(
          () => start.reset(),
        ),
    });
  }

  function respond(id: string | undefined) {
    return (sentAnswer: SentAnswer) => {
      if (id !== undefined && !answer.isPending) {
        answer.mutate({ conversationId: id, ...sentAnswer });
      }
    };
  }

  if (conversationId === undefined) {
    return openingQuery(start, send, respond, restart);
  }
  if (conversation.isPending) {
    return { screen: "loading" };
  }
  if (conversation.isError) {
    return { screen: "not-found", restart };
  }
  const delivery = deliveryOf(answer, conversationId);
  return {
    screen: "conversation",
    view: {
      messages: conversation.data.messages,
      language: conversation.data.language,
      waiting: delivery.outgoing !== null,
      ...delivery,
    },
    answer: respond(conversationId),
    restart,
  };
}
