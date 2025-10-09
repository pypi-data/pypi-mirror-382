# Copyright 2016- Game Server Services, Inc. or its affiliates. All Rights
# Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# A copy of the License is located at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# or in the "license" file accompanying this file. This file is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.
from __future__ import annotations
from typing import *

from ...core.model import CdkResource, Stack
from ...core.func import GetAttr
from ...core.model import TransactionSetting
from ...core.model import ScriptSetting
from ...core.model import NotificationSetting
from ...core.model import LogSetting

from ..ref.NamespaceRef import NamespaceRef
from .CurrentMasterData import CurrentMasterData
from .CategoryModel import CategoryModel

from .options.NamespaceOptions import NamespaceOptions


class Namespace(CdkResource):
    stack: Stack
    name: str
    description: Optional[str] = None
    transaction_setting: Optional[TransactionSetting] = None
    allow_create_room: Optional[bool] = None
    message_life_time_days: Optional[int] = None
    post_message_script: Optional[ScriptSetting] = None
    create_room_script: Optional[ScriptSetting] = None
    delete_room_script: Optional[ScriptSetting] = None
    subscribe_room_script: Optional[ScriptSetting] = None
    unsubscribe_room_script: Optional[ScriptSetting] = None
    post_notification: Optional[NotificationSetting] = None
    log_setting: Optional[LogSetting] = None

    def __init__(
        self,
        stack: Stack,
        name: str,
        options: Optional[NamespaceOptions] = NamespaceOptions(),
    ):
        super().__init__(
            "Chat_Namespace_" + name
        )

        self.stack = stack
        self.name = name
        self.description = options.description if options.description else None
        self.transaction_setting = options.transaction_setting if options.transaction_setting else None
        self.allow_create_room = options.allow_create_room if options.allow_create_room else None
        self.message_life_time_days = options.message_life_time_days if options.message_life_time_days else None
        self.post_message_script = options.post_message_script if options.post_message_script else None
        self.create_room_script = options.create_room_script if options.create_room_script else None
        self.delete_room_script = options.delete_room_script if options.delete_room_script else None
        self.subscribe_room_script = options.subscribe_room_script if options.subscribe_room_script else None
        self.unsubscribe_room_script = options.unsubscribe_room_script if options.unsubscribe_room_script else None
        self.post_notification = options.post_notification if options.post_notification else None
        self.log_setting = options.log_setting if options.log_setting else None
        stack.add_resource(
            self,
        )


    def alternate_keys(
        self,
    ):
        return "name"

    def resource_type(
        self,
    ) -> str:
        return "GS2::Chat::Namespace"

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.name is not None:
            properties["Name"] = self.name
        if self.description is not None:
            properties["Description"] = self.description
        if self.transaction_setting is not None:
            properties["TransactionSetting"] = self.transaction_setting.properties(
            )
        if self.allow_create_room is not None:
            properties["AllowCreateRoom"] = self.allow_create_room
        if self.message_life_time_days is not None:
            properties["MessageLifeTimeDays"] = self.message_life_time_days
        if self.post_message_script is not None:
            properties["PostMessageScript"] = self.post_message_script.properties(
            )
        if self.create_room_script is not None:
            properties["CreateRoomScript"] = self.create_room_script.properties(
            )
        if self.delete_room_script is not None:
            properties["DeleteRoomScript"] = self.delete_room_script.properties(
            )
        if self.subscribe_room_script is not None:
            properties["SubscribeRoomScript"] = self.subscribe_room_script.properties(
            )
        if self.unsubscribe_room_script is not None:
            properties["UnsubscribeRoomScript"] = self.unsubscribe_room_script.properties(
            )
        if self.post_notification is not None:
            properties["PostNotification"] = self.post_notification.properties(
            )
        if self.log_setting is not None:
            properties["LogSetting"] = self.log_setting.properties(
            )

        return properties

    def ref(
        self,
    ) -> NamespaceRef:
        return NamespaceRef(
            self.name,
        )

    def get_attr_namespace_id(
        self,
    ) -> GetAttr:
        return GetAttr(
            self,
            "Item.NamespaceId",
            None,
        )

    def master_data(
        self,
        category_models: List[CategoryModel],
    ) -> Namespace:
        CurrentMasterData(
            self.stack,
            self.name,
            category_models,
        ).add_depends_on(
            self,
        )
        return self
