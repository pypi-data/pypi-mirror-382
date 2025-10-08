# This file is part of monday-client.
#
# Copyright (C) 2024 Leet Cyber Security <https://leetcybersecurity.com/>
#
# monday-client is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# monday-client is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with monday-client. If not, see <https://www.gnu.org/licenses/>.

"""
Monday.com API board type definitions and structures.

This module contains dataclasses that represent Monday.com board objects,
including boards, board views, activity logs, and related operations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from monday.types.column import Column
    from monday.types.group import Group
    from monday.types.item import Item
    from monday.types.user import User
    from monday.types.workspace import Workspace


@dataclass
class Board:
    """
    Represents a Monday.com board with all its properties and relationships.

    This dataclass maps to the Monday.com API board object structure, containing
    fields like name, description, columns, groups, and associated users.

    See Also:
        https://developer.monday.com/api-reference/reference/boards#fields

    """

    activity_logs: list[dict[str, Any]] | None = None
    """The board's activity logs"""

    board_folder_id: str = ''
    """The board's folder unique identifier"""

    board_kind: str = ''
    """The board's kind"""

    columns: list[Column] | None = None
    """The board's columns"""

    communication: str = ''
    """The board's communication"""

    created_at: str = ''
    """The board's creation date. Returned as ``YYYY-MM-DDTHH:MM:SS``"""

    creator: User | None = None
    """The board's creator"""

    creator_id: str = ''
    """The board's creator unique identifier"""

    description: str = ''
    """The board's description"""

    groups: list[Group] | None = None
    """The board's groups"""

    id: str = ''
    """The board's unique identifier"""

    items: list[Item] | None = None
    """The board's items"""

    items_count: int = 0
    """The number of items on the board"""

    name: str = ''
    """The board's name"""

    owners: list[User] | None = None
    """The board's owners"""

    permissions: str = ''
    """The board's permissions"""

    pos: str = ''
    """The board's position"""

    state: str = ''
    """The board's state"""

    subscribers: list[User] | None = None
    """The board's subscribers"""

    tags: list[dict[str, Any]] | None = None
    """The board's tags"""

    top_group: Group | None = None
    """The board's top group"""

    type: str = ''
    """The board's type"""

    updated_at: str = ''
    """The board's last update date. Returned as ``YYYY-MM-DDTHH:MM:SS``"""

    workspace: Workspace | None = None
    """The board's workspace"""

    workspace_id: str = ''
    """The board's workspace unique identifier"""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API requests."""

        def _convert_list(items: list, converter_name: str = 'to_dict') -> list:
            """Convert list items using their converter method if available."""
            return [
                getattr(item, converter_name)()
                if hasattr(item, converter_name)
                else item
                for item in items
            ]

        data = {
            'activity_logs': self.activity_logs,
            'board_folder_id': self.board_folder_id,
            'board_kind': self.board_kind,
            'columns': _convert_list(self.columns) if self.columns else None,
            'communication': self.communication,
            'created_at': self.created_at,
            'creator': self.creator.to_dict() if self.creator else None,
            'creator_id': self.creator_id,
            'description': self.description,
            'groups': _convert_list(self.groups) if self.groups else None,
            'id': self.id,
            'items': _convert_list(self.items) if self.items else None,
            'items_count': self.items_count,
            'name': self.name,
            'owners': _convert_list(self.owners) if self.owners else None,
            'permissions': self.permissions,
            'pos': self.pos,
            'state': self.state,
            'subscribers': _convert_list(self.subscribers)
            if self.subscribers
            else None,
            'tags': self.tags,
            'top_group': self.top_group.to_dict() if self.top_group else None,
            'type': self.type,
            'updated_at': self.updated_at,
            'workspace': self.workspace.to_dict() if self.workspace else None,
            'workspace_id': self.workspace_id,
        }

        return {k: v for k, v in data.items() if v}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Board:
        """Create from dictionary."""
        from monday.types.column import Column  # noqa: PLC0415
        from monday.types.group import Group  # noqa: PLC0415
        from monday.types.item import Item  # noqa: PLC0415
        from monday.types.user import User  # noqa: PLC0415
        from monday.types.workspace import Workspace  # noqa: PLC0415

        items = None
        if data.get('items'):
            items = [
                Item.from_dict(item) if isinstance(item, dict) else item
                for item in data.get('items', [])
            ]

        return cls(
            activity_logs=data.get('activity_logs'),
            board_folder_id=str(data.get('board_folder_id', '')),
            board_kind=str(data.get('board_kind', '')),
            columns=[
                Column.from_dict(column) if hasattr(Column, 'from_dict') else column
                for column in data.get('columns', [])
            ]
            if data.get('columns')
            else None,
            communication=str(data.get('communication', '')),
            created_at=str(data.get('created_at', '')),
            creator=User.from_dict(data['creator']) if data.get('creator') else None,
            creator_id=str(data.get('creator_id', '')),
            description=str(data.get('description', '')),
            groups=[
                Group.from_dict(group) if hasattr(Group, 'from_dict') else group
                for group in data.get('groups', [])
            ]
            if data.get('groups')
            else None,
            id=str(data.get('id', '')),
            items=items,
            items_count=int(data.get('items_count', 0)),
            name=str(data.get('name', '')),
            owners=[
                User.from_dict(owner) if hasattr(User, 'from_dict') else owner
                for owner in data.get('owners', [])
            ]
            if data.get('owners')
            else None,
            permissions=str(data.get('permissions', '')),
            pos=str(data.get('pos', '')),
            state=str(data.get('state', '')),
            subscribers=[
                User.from_dict(subscriber) if hasattr(User, 'from_dict') else subscriber
                for subscriber in data.get('subscribers', [])
            ]
            if data.get('subscribers')
            else None,
            tags=data.get('tags'),
            top_group=Group.from_dict(data['top_group'])
            if data.get('top_group')
            else None,
            type=str(data.get('type', '')),
            updated_at=str(data.get('updated_at', '')),
            workspace=Workspace.from_dict(data['workspace'])
            if data.get('workspace')
            else None,
            workspace_id=str(data.get('workspace_id', '')),
        )


@dataclass
class ActivityLog:
    """
    Type definitions for monday.com API activity log structures.

    These types correspond to Monday.com's activity log view fields as documented in their API reference:
    https://developer.monday.com/api-reference/reference/activity-logs#fields
    """

    account_id: str = ''
    """The unique identifier of the account that initiated the event"""

    data: str = ''
    """The item's column values"""

    entity: Literal['board', 'pulse'] | None = None
    """The entity of the event that was changed"""

    event: str = ''
    """The action that took place"""

    id: str = ''
    """The unique identifier of the activity log event"""

    user_id: str = ''
    """The unique identifier of the user who initiated the event"""

    created_at: str = ''
    """The time of the event in 17-digit unix time"""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API requests."""
        result = {}

        if self.account_id:
            result['account_id'] = self.account_id
        if self.data:
            result['data'] = self.data
        if self.entity:
            result['entity'] = self.entity
        if self.event:
            result['event'] = self.event
        if self.id:
            result['id'] = self.id
        if self.user_id:
            result['user_id'] = self.user_id
        if self.created_at:
            result['created_at'] = self.created_at

        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ActivityLog:
        """Create from dictionary."""
        return cls(
            account_id=str(data.get('account_id', '')),
            data=str(data.get('data', '')),
            entity=data.get('entity'),
            event=str(data.get('event', '')),
            id=str(data.get('id', '')),
            user_id=str(data.get('user_id', '')),
            created_at=str(data.get('created_at', '')),
        )


@dataclass
class BoardView:
    """
    Type definitions for monday.com API board view structures.

    These types correspond to Monday.com's board view fields as documented in their API reference:
    https://developer.monday.com/api-reference/reference/board-views#fields
    """

    id: str = ''
    """The view's unique identifier"""

    name: str = ''
    """The view's name"""

    settings_str: str = ''
    """The view's settings"""

    type: str = ''
    """The view's type"""

    view_specific_data_str: str = ''
    """Specific board view data (only supported for forms)"""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API requests."""
        result = {}

        if self.id:
            result['id'] = self.id
        if self.name:
            result['name'] = self.name
        if self.settings_str:
            result['settings_str'] = self.settings_str
        if self.type:
            result['type'] = self.type
        if self.view_specific_data_str:
            result['view_specific_data_str'] = self.view_specific_data_str

        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BoardView:
        """Create from dictionary."""
        return cls(
            id=str(data.get('id', '')),
            name=str(data.get('name', '')),
            settings_str=str(data.get('settings_str', '')),
            type=str(data.get('type', '')),
            view_specific_data_str=str(data.get('view_specific_data_str', '')),
        )


@dataclass
class UndoData:
    """
    Structure containing undo information for board operations.

    Example:
        .. code-block:: python

            undo_data = {
                'undo_record_id': 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee',
                'action_type': 'modify_project',
                'entity_type': 'Board',
                'entity_id': 987654321,
                'count': 1,
            }

    """

    undo_record_id: str = ''
    """Unique identifier for the undo record"""

    action_type: str = ''
    """Type of action performed (e.g., 'modify_project')"""

    entity_type: str = ''
    """Type of entity modified (e.g., 'Board')"""

    entity_id: str = ''
    """ID of the entity that was modified"""

    count: int = 0
    """Number of entities affected by the operation"""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API requests."""
        result = {}

        if self.undo_record_id:
            result['undo_record_id'] = self.undo_record_id
        if self.action_type:
            result['action_type'] = self.action_type
        if self.entity_type:
            result['entity_type'] = self.entity_type
        if self.entity_id:
            result['entity_id'] = str(self.entity_id)
        if self.count:
            result['count'] = self.count

        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> UndoData:
        """Create from dictionary."""
        return cls(
            undo_record_id=str(data.get('undo_record_id', '')),
            action_type=str(data.get('action_type', '')),
            entity_type=str(data.get('entity_type', '')),
            entity_id=str(data.get('entity_id', '')),
            count=int(data.get('count', 0)),
        )


@dataclass
class UpdateBoard:
    """
    Response structure for board update operations.

    Example:
        .. code-block:: python

            response = {
                'success': True,
                'undo_data': {
                    'undo_record_id': 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee',
                    'action_type': 'modify_project',
                    'entity_type': 'Board',
                    'entity_id': 987654321,
                    'count': 1,
                },
            }

    """

    id: str = ''
    """The id of the updated board"""

    name: str = ''
    """The name of the updated board"""

    updated_attribute: str = ''
    """The value of the updated attribute"""

    previous_attribute: str | None = None
    """The value of the attribute before it was updated"""

    success: bool = False
    """Whether the update operation was successful"""

    undo_data: UndoData | None = None
    """Information needed to undo the update operation"""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API requests."""
        result = {}

        if self.id:
            result['id'] = self.id
        if self.name:
            result['name'] = self.name
        if self.updated_attribute:
            result['updated_attribute'] = self.updated_attribute
        if self.previous_attribute:
            result['previous_attribute'] = self.previous_attribute
        if self.success:
            result['success'] = self.success
        if self.undo_data:
            result['undo_data'] = self.undo_data.to_dict()

        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> UpdateBoard:
        """Create from dictionary."""
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            updated_attribute=data.get('updated_attribute', ''),
            previous_attribute=data.get('previous_attribute', ''),
            success=data.get('success', False),
            undo_data=UndoData.from_dict(data['undo_data'])
            if data.get('undo_data')
            else None,
        )
