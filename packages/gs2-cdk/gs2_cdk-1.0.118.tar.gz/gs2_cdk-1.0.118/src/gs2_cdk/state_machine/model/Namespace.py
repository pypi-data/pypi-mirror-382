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
#
# deny overwrite

from __future__ import annotations
from typing import *

import gs2_cdk.script
from ...core.model import CdkResource, Stack
from ...core.func import GetAttr
from ...core.model import ScriptSetting
from ...core.model import LogSetting

from ..ref.NamespaceRef import NamespaceRef
from ..integration import StateMachineDefinition
from ..model.StateMachineMaster import StateMachineMaster

from .options.NamespaceOptions import NamespaceOptions


class Namespace(CdkResource):
    stack: Stack
    name: str
    description: Optional[str] = None
    start_script: Optional[ScriptSetting] = None
    pass_script: Optional[ScriptSetting] = None
    error_script: Optional[ScriptSetting] = None
    lowest_state_machine_version: Optional[int] = None
    log_setting: Optional[LogSetting] = None

    def __init__(
        self,
        stack: Stack,
        name: str,
        options: Optional[NamespaceOptions] = NamespaceOptions(),
    ):
        super().__init__(
            "StateMachine_Namespace_" + name
        )

        self.stack = stack
        self.name = name
        self.description = options.description if options.description else None
        self.start_script = options.start_script if options.start_script else None
        self.pass_script = options.pass_script if options.pass_script else None
        self.error_script = options.error_script if options.error_script else None
        self.lowest_state_machine_version = options.lowest_state_machine_version if options.lowest_state_machine_version else None
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
        return "GS2::StateMachine::Namespace"

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.name is not None:
            properties["Name"] = self.name
        if self.description is not None:
            properties["Description"] = self.description
        if self.start_script is not None:
            properties["StartScript"] = self.start_script.properties(
            )
        if self.pass_script is not None:
            properties["PassScript"] = self.pass_script.properties(
            )
        if self.error_script is not None:
            properties["ErrorScript"] = self.error_script.properties(
            )
        if self.lowest_state_machine_version is not None:
            properties["LowestStateMachineVersion"] = self.lowest_state_machine_version
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
            None,
            None,
            "Item.NamespaceId",
        )

    def state_machine(
            self,
            script_namespace: gs2_cdk.script.Namespace,
            definition: StateMachineDefinition,
    ):
        definition.append_scripts(
            self.stack,
            script_namespace=script_namespace,
        )
        StateMachineMaster(
            self.stack,
            namespace_name=self.name,
            main_state_machine_name=definition.state_machine_name,
            payload=definition.gsl().replace("{scriptNamespaceName}", script_namespace.name),
        ).add_depends_on(
            self,
        )
