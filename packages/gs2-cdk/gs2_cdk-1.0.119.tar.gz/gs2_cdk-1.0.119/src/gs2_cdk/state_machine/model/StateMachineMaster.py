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

from ...core.model import CdkResource, Stack
from ...core.func import GetAttr

from ..ref.StateMachineMasterRef import StateMachineMasterRef

from .options.StateMachineMasterOptions import StateMachineMasterOptions


class StateMachineMaster(CdkResource):
    stack: Stack
    namespace_name: str
    main_state_machine_name: str
    payload: str

    def __init__(
        self,
        stack: Stack,
        namespace_name: str,
        main_state_machine_name: str,
        payload: str,
        options: Optional[StateMachineMasterOptions] = StateMachineMasterOptions(),
    ):
        super().__init__(
            "StateMachine_StateMachineMaster_" + namespace_name
        )

        self.stack = stack
        self.namespace_name = namespace_name
        self.main_state_machine_name = main_state_machine_name
        self.payload = payload
        stack.add_resource(
            self,
        )


    def alternate_keys(
        self,
    ):
        return "version"

    def resource_type(
        self,
    ) -> str:
        return "GS2::StateMachine::StateMachineMaster"

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.namespace_name is not None:
            properties["NamespaceName"] = self.namespace_name
        if self.main_state_machine_name is not None:
            properties["MainStateMachineName"] = self.main_state_machine_name
        if self.payload is not None:
            properties["Payload"] = self.payload

        return properties

    def ref(
        self,
        version: int,
    ) -> StateMachineMasterRef:
        return StateMachineMasterRef(
            self.namespace_name,
            version,
        )

    def get_attr_state_machine_id(
        self,
    ) -> GetAttr:
        return GetAttr(
            None,
            None,
            "Item.StateMachineId",
        )
