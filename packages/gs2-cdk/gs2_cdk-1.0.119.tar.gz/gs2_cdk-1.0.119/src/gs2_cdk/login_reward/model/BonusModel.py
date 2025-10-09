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
from .Reward import Reward
from ...core.model import VerifyAction
from ...core.model import ConsumeAction
from .options.BonusModelOptions import BonusModelOptions
from .options.BonusModelModeIsScheduleOptions import BonusModelModeIsScheduleOptions
from .options.BonusModelModeIsStreamingOptions import BonusModelModeIsStreamingOptions
from .options.BonusModelMissedReceiveReliefIsEnabledOptions import BonusModelMissedReceiveReliefIsEnabledOptions
from .options.BonusModelMissedReceiveReliefIsDisabledOptions import BonusModelMissedReceiveReliefIsDisabledOptions
from .enums.BonusModelMode import BonusModelMode
from .enums.BonusModelRepeat import BonusModelRepeat
from .enums.BonusModelMissedReceiveRelief import BonusModelMissedReceiveRelief


class BonusModel:
    name: str
    mode: BonusModelMode
    missed_receive_relief: BonusModelMissedReceiveRelief
    metadata: Optional[str] = None
    period_event_id: Optional[str] = None
    reset_hour: Optional[int] = None
    repeat: Optional[BonusModelRepeat] = None
    rewards: Optional[List[Reward]] = None
    missed_receive_relief_verify_actions: Optional[List[VerifyAction]] = None
    missed_receive_relief_consume_actions: Optional[List[ConsumeAction]] = None

    def __init__(
        self,
        name: str,
        mode: BonusModelMode,
        missed_receive_relief: BonusModelMissedReceiveRelief,
        options: Optional[BonusModelOptions] = BonusModelOptions(),
    ):
        self.name = name
        self.mode = mode
        self.missed_receive_relief = missed_receive_relief
        self.metadata = options.metadata if options.metadata else None
        self.period_event_id = options.period_event_id if options.period_event_id else None
        self.reset_hour = options.reset_hour if options.reset_hour else None
        self.repeat = options.repeat if options.repeat else None
        self.rewards = options.rewards if options.rewards else None
        self.missed_receive_relief_verify_actions = options.missed_receive_relief_verify_actions if options.missed_receive_relief_verify_actions else None
        self.missed_receive_relief_consume_actions = options.missed_receive_relief_consume_actions if options.missed_receive_relief_consume_actions else None

    @staticmethod
    def mode_is_schedule(
        name: str,
        missed_receive_relief: BonusModelMissedReceiveRelief,
        options: Optional[BonusModelModeIsScheduleOptions] = BonusModelModeIsScheduleOptions(),
    ) -> BonusModel:
        return BonusModel(
            name,
            BonusModelMode.SCHEDULE,
            missed_receive_relief,
            BonusModelOptions(
                options.metadata,
                options.period_event_id,
                options.rewards,
                options.missed_receive_relief_verify_actions,
                options.missed_receive_relief_consume_actions,
            ),
        )

    @staticmethod
    def mode_is_streaming(
        name: str,
        missed_receive_relief: BonusModelMissedReceiveRelief,
        repeat: BonusModelRepeat,
        options: Optional[BonusModelModeIsStreamingOptions] = BonusModelModeIsStreamingOptions(),
    ) -> BonusModel:
        return BonusModel(
            name,
            BonusModelMode.STREAMING,
            missed_receive_relief,
            BonusModelOptions(
                repeat,
                options.metadata,
                options.period_event_id,
                options.rewards,
                options.missed_receive_relief_verify_actions,
                options.missed_receive_relief_consume_actions,
            ),
        )

    @staticmethod
    def missed_receive_relief_is_enabled(
        name: str,
        mode: BonusModelMode,
        options: Optional[BonusModelMissedReceiveReliefIsEnabledOptions] = BonusModelMissedReceiveReliefIsEnabledOptions(),
    ) -> BonusModel:
        return BonusModel(
            name,
            mode,
            BonusModelMissedReceiveRelief.ENABLED,
            BonusModelOptions(
                options.metadata,
                options.period_event_id,
                options.rewards,
                options.missed_receive_relief_verify_actions,
                options.missed_receive_relief_consume_actions,
            ),
        )

    @staticmethod
    def missed_receive_relief_is_disabled(
        name: str,
        mode: BonusModelMode,
        options: Optional[BonusModelMissedReceiveReliefIsDisabledOptions] = BonusModelMissedReceiveReliefIsDisabledOptions(),
    ) -> BonusModel:
        return BonusModel(
            name,
            mode,
            BonusModelMissedReceiveRelief.DISABLED,
            BonusModelOptions(
                options.metadata,
                options.period_event_id,
                options.rewards,
                options.missed_receive_relief_verify_actions,
                options.missed_receive_relief_consume_actions,
            ),
        )

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.name is not None:
            properties["name"] = self.name
        if self.metadata is not None:
            properties["metadata"] = self.metadata
        if self.mode is not None:
            properties["mode"] = self.mode.value
        if self.period_event_id is not None:
            properties["periodEventId"] = self.period_event_id
        if self.reset_hour is not None:
            properties["resetHour"] = self.reset_hour
        if self.repeat is not None:
            properties["repeat"] = self.repeat.value
        if self.rewards is not None:
            properties["rewards"] = [
                v.properties(
                )
                for v in self.rewards
            ]
        if self.missed_receive_relief is not None:
            properties["missedReceiveRelief"] = self.missed_receive_relief.value
        if self.missed_receive_relief_verify_actions is not None:
            properties["missedReceiveReliefVerifyActions"] = [
                v.properties(
                )
                for v in self.missed_receive_relief_verify_actions
            ]
        if self.missed_receive_relief_consume_actions is not None:
            properties["missedReceiveReliefConsumeActions"] = [
                v.properties(
                )
                for v in self.missed_receive_relief_consume_actions
            ]

        return properties
