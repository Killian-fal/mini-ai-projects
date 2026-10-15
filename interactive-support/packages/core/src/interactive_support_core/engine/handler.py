from interactive_support_flow_api._internal import InternalError
from interactive_support_flow_api import InvalidAnswer
from interactive_support_flow_api.model.flow import AskStep, End, Flow, StepId
from interactive_support_flow_api.model.context import FlowContext
from interactive_support_core.engine.bucket import MessageBucket
from interactive_support_core.engine.flow_helper import (
    find_flow,
    find_step,
    find_ask_step,
    determine_next_step,
)
from interactive_support_core.model import Conversation, MessageActionResponse


def start_flow(conversation: Conversation):
    if conversation.issue is None or conversation.order_number is None:
        raise InternalError("CONVERSATION_NOT_OPENED")

    flow = find_flow(conversation.issue)
    conversation.context = FlowContext(
        issue=conversation.issue,
        order_number=conversation.order_number,
        language=conversation.language,
    )
    _advance(
        conversation, flow, conversation.context, MessageBucket(), flow.steps[0].id
    )


def flow_handler(message: MessageActionResponse, conversation: Conversation):
    if conversation.context is None:
        raise InternalError("FLOW_NOT_STARTED")

    flow = find_flow(conversation.context.issue)
    step = find_ask_step(flow, message.action_id)

    ctx = conversation.context.model_copy(deep=True)
    bucket = MessageBucket()
    try:
        returned_value = step.run(
            ctx, step.question(ctx).parse(message.response), bucket
        )
    except InvalidAnswer as e:
        error = MessageBucket()
        error.add_code(e.error_code)
        conversation.messages.extend(error.messages)
        return  # the action is still pending: the same question is asked again, without its pre_hook

    conversation.context = ctx
    conversation.complete_action(message.action_id)
    _advance(conversation, flow, ctx, bucket, determine_next_step(step, returned_value))


def _advance(
    conversation: Conversation,
    flow: Flow,
    ctx: FlowContext,
    bucket: MessageBucket,
    target: StepId | End,
):
    try:
        while isinstance(target, StepId):
            step = find_step(flow, target)
            if step.pre_hook:
                step.pre_hook(ctx, bucket)

            if isinstance(step, AskStep):
                conversation.actions.add(
                    flow.action_id(step.id), step.question(ctx).action()
                )
                return

            returned_value = step.run(ctx, bucket)
            target = determine_next_step(step, returned_value)
    finally:
        conversation.messages.extend(bucket.messages)
