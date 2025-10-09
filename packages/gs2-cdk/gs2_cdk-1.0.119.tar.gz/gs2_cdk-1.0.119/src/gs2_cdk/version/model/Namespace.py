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
from ...core.model import LogSetting

from ..ref.NamespaceRef import NamespaceRef
from .CurrentMasterData import CurrentMasterData
from .VersionModel import VersionModel

from .options.NamespaceOptions import NamespaceOptions


class Namespace(CdkResource):
    stack: Stack
    name: str
    assume_user_id: str
    description: Optional[str] = None
    transaction_setting: Optional[TransactionSetting] = None
    accept_version_script: Optional[ScriptSetting] = None
    check_version_trigger_script_id: Optional[str] = None
    log_setting: Optional[LogSetting] = None

    def __init__(
        self,
        stack: Stack,
        name: str,
        assume_user_id: str,
        options: Optional[NamespaceOptions] = NamespaceOptions(),
    ):
        super().__init__(
            "Version_Namespace_" + name
        )

        self.stack = stack
        self.name = name
        self.assume_user_id = assume_user_id
        self.description = options.description if options.description else None
        self.transaction_setting = options.transaction_setting if options.transaction_setting else None
        self.accept_version_script = options.accept_version_script if options.accept_version_script else None
        self.check_version_trigger_script_id = options.check_version_trigger_script_id if options.check_version_trigger_script_id else None
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
        return "GS2::Version::Namespace"

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
        if self.assume_user_id is not None:
            properties["AssumeUserId"] = self.assume_user_id
        if self.accept_version_script is not None:
            properties["AcceptVersionScript"] = self.accept_version_script.properties(
            )
        if self.check_version_trigger_script_id is not None:
            properties["CheckVersionTriggerScriptId"] = self.check_version_trigger_script_id
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
        version_models: List[VersionModel],
    ) -> Namespace:
        CurrentMasterData(
            self.stack,
            self.name,
            version_models,
        ).add_depends_on(
            self,
        )
        return self
