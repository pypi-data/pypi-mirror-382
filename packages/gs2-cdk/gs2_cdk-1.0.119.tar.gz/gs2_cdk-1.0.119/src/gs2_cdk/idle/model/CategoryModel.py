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
from ...core.model import AcquireAction
from .AcquireActionList import AcquireActionList
from .options.CategoryModelOptions import CategoryModelOptions
from .enums.CategoryModelRewardResetMode import CategoryModelRewardResetMode


class CategoryModel:
    name: str
    reward_interval_minutes: int
    default_maximum_idle_minutes: int
    reward_reset_mode: CategoryModelRewardResetMode
    acquire_actions: List[AcquireActionList]
    metadata: Optional[str] = None
    idle_period_schedule_id: Optional[str] = None
    receive_period_schedule_id: Optional[str] = None

    def __init__(
        self,
        name: str,
        reward_interval_minutes: int,
        default_maximum_idle_minutes: int,
        reward_reset_mode: CategoryModelRewardResetMode,
        acquire_actions: List[AcquireActionList],
        options: Optional[CategoryModelOptions] = CategoryModelOptions(),
    ):
        self.name = name
        self.reward_interval_minutes = reward_interval_minutes
        self.default_maximum_idle_minutes = default_maximum_idle_minutes
        self.reward_reset_mode = reward_reset_mode
        self.acquire_actions = acquire_actions
        self.metadata = options.metadata if options.metadata else None
        self.idle_period_schedule_id = options.idle_period_schedule_id if options.idle_period_schedule_id else None
        self.receive_period_schedule_id = options.receive_period_schedule_id if options.receive_period_schedule_id else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.name is not None:
            properties["name"] = self.name
        if self.metadata is not None:
            properties["metadata"] = self.metadata
        if self.reward_interval_minutes is not None:
            properties["rewardIntervalMinutes"] = self.reward_interval_minutes
        if self.default_maximum_idle_minutes is not None:
            properties["defaultMaximumIdleMinutes"] = self.default_maximum_idle_minutes
        if self.reward_reset_mode is not None:
            properties["rewardResetMode"] = self.reward_reset_mode.value
        if self.acquire_actions is not None:
            properties["acquireActions"] = [
                v.properties(
                )
                for v in self.acquire_actions
            ]
        if self.idle_period_schedule_id is not None:
            properties["idlePeriodScheduleId"] = self.idle_period_schedule_id
        if self.receive_period_schedule_id is not None:
            properties["receivePeriodScheduleId"] = self.receive_period_schedule_id

        return properties
