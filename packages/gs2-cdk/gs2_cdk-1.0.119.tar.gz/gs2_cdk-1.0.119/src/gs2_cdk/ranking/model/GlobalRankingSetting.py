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
from .FixedTiming import FixedTiming
from .Scope import Scope
from .options.GlobalRankingSettingOptions import GlobalRankingSettingOptions


class GlobalRankingSetting:
    unique_by_user_id: bool
    calculate_interval_minutes: int
    calculate_fixed_timing: Optional[FixedTiming] = None
    additional_scopes: Optional[List[Scope]] = None
    ignore_user_ids: Optional[List[str]] = None
    generation: Optional[str] = None

    def __init__(
        self,
        unique_by_user_id: bool,
        calculate_interval_minutes: int,
        options: Optional[GlobalRankingSettingOptions] = GlobalRankingSettingOptions(),
    ):
        self.unique_by_user_id = unique_by_user_id
        self.calculate_interval_minutes = calculate_interval_minutes
        self.calculate_fixed_timing = options.calculate_fixed_timing if options.calculate_fixed_timing else None
        self.additional_scopes = options.additional_scopes if options.additional_scopes else None
        self.ignore_user_ids = options.ignore_user_ids if options.ignore_user_ids else None
        self.generation = options.generation if options.generation else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.unique_by_user_id is not None:
            properties["uniqueByUserId"] = self.unique_by_user_id
        if self.calculate_interval_minutes is not None:
            properties["calculateIntervalMinutes"] = self.calculate_interval_minutes
        if self.calculate_fixed_timing is not None:
            properties["calculateFixedTiming"] = self.calculate_fixed_timing.properties(
            )
        if self.additional_scopes is not None:
            properties["additionalScopes"] = [
                v.properties(
                )
                for v in self.additional_scopes
            ]
        if self.ignore_user_ids is not None:
            properties["ignoreUserIds"] = self.ignore_user_ids
        if self.generation is not None:
            properties["generation"] = self.generation

        return properties
