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
from .MissionGroupModel import MissionGroupModel
from .CounterModel import CounterModel

from .options.NamespaceOptions import NamespaceOptions


class Namespace(CdkResource):
    stack: Stack
    name: str
    description: Optional[str] = None
    transaction_setting: Optional[TransactionSetting] = None
    mission_complete_script: Optional[ScriptSetting] = None
    counter_increment_script: Optional[ScriptSetting] = None
    receive_rewards_script: Optional[ScriptSetting] = None
    complete_notification: Optional[NotificationSetting] = None
    log_setting: Optional[LogSetting] = None

    def __init__(
        self,
        stack: Stack,
        name: str,
        options: Optional[NamespaceOptions] = NamespaceOptions(),
    ):
        super().__init__(
            "Mission_Namespace_" + name
        )

        self.stack = stack
        self.name = name
        self.description = options.description if options.description else None
        self.transaction_setting = options.transaction_setting if options.transaction_setting else None
        self.mission_complete_script = options.mission_complete_script if options.mission_complete_script else None
        self.counter_increment_script = options.counter_increment_script if options.counter_increment_script else None
        self.receive_rewards_script = options.receive_rewards_script if options.receive_rewards_script else None
        self.complete_notification = options.complete_notification if options.complete_notification else None
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
        return "GS2::Mission::Namespace"

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
        if self.mission_complete_script is not None:
            properties["MissionCompleteScript"] = self.mission_complete_script.properties(
            )
        if self.counter_increment_script is not None:
            properties["CounterIncrementScript"] = self.counter_increment_script.properties(
            )
        if self.receive_rewards_script is not None:
            properties["ReceiveRewardsScript"] = self.receive_rewards_script.properties(
            )
        if self.complete_notification is not None:
            properties["CompleteNotification"] = self.complete_notification.properties(
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
        groups: List[MissionGroupModel],
        counters: List[CounterModel],
    ) -> Namespace:
        CurrentMasterData(
            self.stack,
            self.name,
            groups,
            counters,
        ).add_depends_on(
            self,
        )
        return self
