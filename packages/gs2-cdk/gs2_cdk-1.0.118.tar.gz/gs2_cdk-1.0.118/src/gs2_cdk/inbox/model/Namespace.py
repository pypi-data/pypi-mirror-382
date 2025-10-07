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
from .GlobalMessage import GlobalMessage

from .options.NamespaceOptions import NamespaceOptions


class Namespace(CdkResource):
    stack: Stack
    name: str
    description: Optional[str] = None
    is_automatic_deleting_enabled: Optional[bool] = None
    transaction_setting: Optional[TransactionSetting] = None
    receive_message_script: Optional[ScriptSetting] = None
    read_message_script: Optional[ScriptSetting] = None
    delete_message_script: Optional[ScriptSetting] = None
    receive_notification: Optional[NotificationSetting] = None
    log_setting: Optional[LogSetting] = None

    def __init__(
        self,
        stack: Stack,
        name: str,
        options: Optional[NamespaceOptions] = NamespaceOptions(),
    ):
        super().__init__(
            "Inbox_Namespace_" + name
        )

        self.stack = stack
        self.name = name
        self.description = options.description if options.description else None
        self.is_automatic_deleting_enabled = options.is_automatic_deleting_enabled if options.is_automatic_deleting_enabled else None
        self.transaction_setting = options.transaction_setting if options.transaction_setting else None
        self.receive_message_script = options.receive_message_script if options.receive_message_script else None
        self.read_message_script = options.read_message_script if options.read_message_script else None
        self.delete_message_script = options.delete_message_script if options.delete_message_script else None
        self.receive_notification = options.receive_notification if options.receive_notification else None
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
        return "GS2::Inbox::Namespace"

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.name is not None:
            properties["Name"] = self.name
        if self.description is not None:
            properties["Description"] = self.description
        if self.is_automatic_deleting_enabled is not None:
            properties["IsAutomaticDeletingEnabled"] = self.is_automatic_deleting_enabled
        if self.transaction_setting is not None:
            properties["TransactionSetting"] = self.transaction_setting.properties(
            )
        if self.receive_message_script is not None:
            properties["ReceiveMessageScript"] = self.receive_message_script.properties(
            )
        if self.read_message_script is not None:
            properties["ReadMessageScript"] = self.read_message_script.properties(
            )
        if self.delete_message_script is not None:
            properties["DeleteMessageScript"] = self.delete_message_script.properties(
            )
        if self.receive_notification is not None:
            properties["ReceiveNotification"] = self.receive_notification.properties(
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
        global_messages: List[GlobalMessage],
    ) -> Namespace:
        CurrentMasterData(
            self.stack,
            self.name,
            global_messages,
        ).add_depends_on(
            self,
        )
        return self
