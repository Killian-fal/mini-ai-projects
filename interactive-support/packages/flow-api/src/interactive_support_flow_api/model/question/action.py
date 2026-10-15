from __future__ import annotations

from collections.abc import Iterator
from enum import Enum

from pydantic import BaseModel

from interactive_support_flow_api._internal import InternalError
from interactive_support_flow_api.model.polymorphic import Polymorphic


class ActionType(Enum):
    GROUP = "GROUP"
    UNIQUE_CHOICE = "UNIQUE_CHOICE"
    TEXT_INPUT = "TEXT_INPUT"
    YES_NO = "YES_NO"
    PHOTO_UPLOAD = "PHOTO_UPLOAD"
    FORM = "FORM"


class Action(Polymorphic):
    type: ActionType


class ActionUniqueChoice(Action):
    type: ActionType = ActionType.UNIQUE_CHOICE
    choices: list[str]


class ActionTextInput(Action):
    type: ActionType = ActionType.TEXT_INPUT


class Location(BaseModel):
    latitude: float
    longitude: float


class ActionYesNo(Action):
    type: ActionType = ActionType.YES_NO
    value: str
    location: Location | None = None


class ActionPhotoUpload(Action):
    type: ActionType = ActionType.PHOTO_UPLOAD


class ActionForm(Action):
    type: ActionType = ActionType.FORM
    fields: dict[str, str]


class ActionGroup(Action):
    type: ActionType = ActionType.GROUP
    children: dict[str, Action]

    def pending(self) -> dict[str, Action]:
        result = {}
        for node_id, node in self.children.items():
            result = result | (
                node.pending() if isinstance(node, ActionGroup) else {node_id: node}
            )
        return result

    def groups(self) -> Iterator[ActionGroup]:
        yield self

        for node in self.children.values():
            if isinstance(node, ActionGroup):
                yield from node.groups()

    def add(self, action_id: str, action: Action):
        if action_id in self.pending():
            raise InternalError(f"ACTION_ALREADY_EXISTS:{action_id}")

        self.children[action_id] = action

    def remove(self, action_id: str):
        parent = self._find_parent(action_id)
        del parent.children[action_id]

    def replace(self, action_id: str, by: dict[str, Action]):
        parent = self._find_parent(action_id)

        new_children = {}
        for child_id, child in parent.children.items():
            if child_id == action_id:
                new_children.update(by)
            else:
                new_children[child_id] = child
        parent.children = new_children

    def _find_parent(self, action_id: str) -> ActionGroup:
        if action_id not in self.pending():
            raise InternalError(f"ACTION_NOT_FOUND:{action_id}")

        return next(group for group in self.groups() if action_id in group.children)
