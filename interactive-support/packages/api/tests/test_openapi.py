"""
The front generates its client and its types from the OpenAPI: a core model returned as is would leave them untyped.
"""

from typing import Any

from fastapi.testclient import TestClient

from interactive_support_api.app import app
from interactive_support_core.model import MessageRole
from interactive_support_flow_api.model.question import ActionType


def openapi() -> dict[str, Any]:
    return TestClient(app).get("/openapi.json").json()


def test_every_message_role_has_its_schema():
    # a new role in core fails here
    messages = openapi()["components"]["schemas"]["ConversationDto"]["properties"][
        "messages"
    ]["items"]

    assert messages["discriminator"]["propertyName"] == "role"
    assert set(messages["discriminator"]["mapping"]) == {
        role.value for role in MessageRole
    }


def test_every_action_type_has_its_schema():
    # a new action type in core fails here
    action = openapi()["components"]["schemas"]["MessageActionDto"]["properties"][
        "action"
    ]

    assert action["discriminator"]["propertyName"] == "type"
    assert set(action["discriminator"]["mapping"]) == {
        action_type.value
        for action_type in ActionType
        if action_type is not ActionType.GROUP
    }  # a group is never shown: the front gets its leaves, one at a time


def test_the_operation_ids_are_the_route_names():
    # a duplicate fails too
    assert sorted(
        operation["operationId"]
        for path in openapi()["paths"].values()
        for operation in path.values()
    ) == [
        "answer",
        "get_conversation",
        "start_conversation",
    ]
