import { skipToken, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { answer, getConversation, startConversation } from "./endpoints";
import { isActionNotFound, isConversationNotFound } from "./errors";
import type { Conversation } from "./types";

const conversationKey = (conversationId: string) => ["conversation", conversationId] as const;

export type AnswerVariables = {
  conversationId: string;
  actionId: string;
  response: string;
};

export function useConversation(conversationId: string | undefined) {
  return useQuery({
    queryKey: conversationKey(conversationId ?? ""),
    queryFn: conversationId === undefined ? skipToken : () => getConversation(conversationId),
    retry: (failures, error) => !isConversationNotFound(error) && failures < 2,
    throwOnError: (error) => !isConversationNotFound(error),
  });
}

export function useStartConversation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (message: string) => startConversation(message),
    onSuccess: (conversation: Conversation) => {
      queryClient.setQueryData(conversationKey(conversation.id), conversation);
    },
  });
}

export function useAnswer() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ conversationId, actionId, response }: AnswerVariables) =>
      answer(conversationId, actionId, response),
    onSuccess: (conversation: Conversation) => {
      queryClient.setQueryData(conversationKey(conversation.id), conversation);
    },
    onError: async (error, { conversationId }) => {
      if (isActionNotFound(error)) {
        await queryClient.invalidateQueries({ queryKey: conversationKey(conversationId) });
      }
    },
  });
}
