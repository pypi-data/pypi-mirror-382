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
from .BuffTargetGrn import BuffTargetGrn
from .options.BuffTargetActionOptions import BuffTargetActionOptions
from .enums.BuffTargetActionTargetActionName import BuffTargetActionTargetActionName


class BuffTargetAction:
    target_action_name: str
    target_field_name: str
    condition_grns: List[BuffTargetGrn]
    rate: float

    def __init__(
        self,
        target_action_name: str,
        target_field_name: str,
        condition_grns: List[BuffTargetGrn],
        rate: float,
        options: Optional[BuffTargetActionOptions] = BuffTargetActionOptions(),
    ):
        self.target_action_name = target_action_name
        self.target_field_name = target_field_name
        self.condition_grns = condition_grns
        self.rate = rate

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.target_action_name is not None:
            properties["targetActionName"] = self.target_action_name.value
        if self.target_field_name is not None:
            properties["targetFieldName"] = self.target_field_name
        if self.condition_grns is not None:
            properties["conditionGrns"] = [
                v.properties(
                )
                for v in self.condition_grns
            ]
        if self.rate is not None:
            properties["rate"] = self.rate

        return properties
