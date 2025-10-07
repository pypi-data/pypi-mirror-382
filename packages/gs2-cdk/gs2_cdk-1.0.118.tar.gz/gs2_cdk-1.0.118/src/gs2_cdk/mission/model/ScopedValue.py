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
from .options.ScopedValueOptions import ScopedValueOptions
from .options.ScopedValueScopeTypeIsResetTimingOptions import ScopedValueScopeTypeIsResetTimingOptions
from .options.ScopedValueScopeTypeIsVerifyActionOptions import ScopedValueScopeTypeIsVerifyActionOptions
from .enums.ScopedValueScopeType import ScopedValueScopeType
from .enums.ScopedValueResetType import ScopedValueResetType


class ScopedValue:
    scope_type: ScopedValueScopeType
    value: int
    reset_type: Optional[ScopedValueResetType] = None
    condition_name: Optional[str] = None
    next_reset_at: Optional[int] = None

    def __init__(
        self,
        scope_type: ScopedValueScopeType,
        value: int,
        options: Optional[ScopedValueOptions] = ScopedValueOptions(),
    ):
        self.scope_type = scope_type
        self.value = value
        self.reset_type = options.reset_type if options.reset_type else None
        self.condition_name = options.condition_name if options.condition_name else None
        self.next_reset_at = options.next_reset_at if options.next_reset_at else None

    @staticmethod
    def scope_type_is_reset_timing(
        value: int,
        updated_at: int,
        reset_type: ScopedValueResetType,
        options: Optional[ScopedValueScopeTypeIsResetTimingOptions] = ScopedValueScopeTypeIsResetTimingOptions(),
    ) -> ScopedValue:
        return ScopedValue(
            ScopedValueScopeType.RESET_TIMING,
            value,
            updated_at,
            ScopedValueOptions(
                reset_type,
                options.next_reset_at,
            ),
        )

    @staticmethod
    def scope_type_is_verify_action(
        value: int,
        updated_at: int,
        condition_name: str,
        options: Optional[ScopedValueScopeTypeIsVerifyActionOptions] = ScopedValueScopeTypeIsVerifyActionOptions(),
    ) -> ScopedValue:
        return ScopedValue(
            ScopedValueScopeType.VERIFY_ACTION,
            value,
            updated_at,
            ScopedValueOptions(
                condition_name,
                options.next_reset_at,
            ),
        )

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.scope_type is not None:
            properties["scopeType"] = self.scope_type.value
        if self.reset_type is not None:
            properties["resetType"] = self.reset_type.value
        if self.condition_name is not None:
            properties["conditionName"] = self.condition_name
        if self.value is not None:
            properties["value"] = self.value

        return properties
