from uuid import uuid4

from interactive_support_core.handler import handle
from interactive_support_core.opening.handler import open_conversation
from interactive_support_core.registry import check_flows
from interactive_support_cli.frontend_handler import frontend_handler
from interactive_support_core.translation import check_translations
from interactive_support_cli.display import print_conversation, print_messages
from interactive_support_observability import trace_session


def start_conversation():
    check_translations()
    check_flows()

    # msg = "Je n'ai pas reçu ma commande, ça fait 2 semaines que j'attends. Je n'ai aucune nouvelle"
    # msg = "Je n'ai pas reçu ma commande, ça fait 2 semaines que j'attends. Je n'ai aucune nouvelle. Elle est en retard."
    # msg = "Bonjour j'ai un probleme avec ma commande numero cma_12345"
    msg = "Bonjour, j'aimerai annuler ma commande cma_001"
    session_id = str(uuid4())
    with trace_session(session_id):
        conversation = open_conversation(msg, session_id)

        shown = 0
        while conversation.actions.pending():
            action_id, action = conversation.ask_next_action()
            shown = print_messages(conversation, shown)
            handle(
                frontend_handler(
                    action_id=action_id, action=action, conversation=conversation
                ),
                conversation,
            )
        print_messages(conversation, shown)

    print()
    print_conversation(conversation)
