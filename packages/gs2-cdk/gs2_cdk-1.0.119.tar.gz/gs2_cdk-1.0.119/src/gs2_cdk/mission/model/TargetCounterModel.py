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
from .options.TargetCounterModelOptions import TargetCounterModelOptions
from .options.TargetCounterModelScopeTypeIsResetTimingOptions import TargetCounterModelScopeTypeIsResetTimingOptions
from .options.TargetCounterModelScopeTypeIsVerifyActionOptions import TargetCounterModelScopeTypeIsVerifyActionOptions
from .enums.TargetCounterModelScopeType import TargetCounterModelScopeType
from .enums.TargetCounterModelResetType import TargetCounterModelResetType


class TargetCounterModel:
    counter_name: str
    scope_type: TargetCounterModelScopeType
    value: int
    reset_type: Optional[TargetCounterModelResetType] = None
    condition_name: Optional[str] = None

    def __init__(
        self,
        counter_name: str,
        scope_type: TargetCounterModelScopeType,
        value: int,
        options: Optional[TargetCounterModelOptions] = TargetCounterModelOptions(),
    ):
        self.counter_name = counter_name
        self.scope_type = scope_type
        self.value = value
        self.reset_type = options.reset_type if options.reset_type else None
        self.condition_name = options.condition_name if options.condition_name else None

    @staticmethod
    def scope_type_is_reset_timing(
        counter_name: str,
        value: int,
        options: Optional[TargetCounterModelScopeTypeIsResetTimingOptions] = TargetCounterModelScopeTypeIsResetTimingOptions(),
    ) -> TargetCounterModel:
        return TargetCounterModel(
            counter_name,
            TargetCounterModelScopeType.RESET_TIMING,
            value,
            TargetCounterModelOptions(
                options.reset_type,
            ),
        )

    @staticmethod
    def scope_type_is_verify_action(
        counter_name: str,
        value: int,
        condition_name: str,
        options: Optional[TargetCounterModelScopeTypeIsVerifyActionOptions] = TargetCounterModelScopeTypeIsVerifyActionOptions(),
    ) -> TargetCounterModel:
        return TargetCounterModel(
            counter_name,
            TargetCounterModelScopeType.VERIFY_ACTION,
            value,
            TargetCounterModelOptions(
                condition_name,
                options.reset_type,
            ),
        )

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.counter_name is not None:
            properties["counterName"] = self.counter_name
        if self.scope_type is not None:
            properties["scopeType"] = self.scope_type.value
        if self.reset_type is not None:
            properties["resetType"] = self.reset_type.value
        if self.condition_name is not None:
            properties["conditionName"] = self.condition_name
        if self.value is not None:
            properties["value"] = self.value

        return properties
