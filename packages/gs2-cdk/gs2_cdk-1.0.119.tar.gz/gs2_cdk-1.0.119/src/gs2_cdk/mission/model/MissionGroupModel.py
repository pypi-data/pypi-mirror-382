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
from .TargetCounterModel import TargetCounterModel
from ...core.model import VerifyAction
from ...core.model import AcquireAction
from .MissionTaskModel import MissionTaskModel
from .options.MissionGroupModelOptions import MissionGroupModelOptions
from .options.MissionGroupModelResetTypeIsNotResetOptions import MissionGroupModelResetTypeIsNotResetOptions
from .options.MissionGroupModelResetTypeIsDailyOptions import MissionGroupModelResetTypeIsDailyOptions
from .options.MissionGroupModelResetTypeIsWeeklyOptions import MissionGroupModelResetTypeIsWeeklyOptions
from .options.MissionGroupModelResetTypeIsMonthlyOptions import MissionGroupModelResetTypeIsMonthlyOptions
from .options.MissionGroupModelResetTypeIsDaysOptions import MissionGroupModelResetTypeIsDaysOptions
from .enums.MissionGroupModelResetType import MissionGroupModelResetType
from .enums.MissionGroupModelResetDayOfWeek import MissionGroupModelResetDayOfWeek


class MissionGroupModel:
    name: str
    reset_type: MissionGroupModelResetType
    metadata: Optional[str] = None
    tasks: Optional[List[MissionTaskModel]] = None
    reset_day_of_month: Optional[int] = None
    reset_day_of_week: Optional[MissionGroupModelResetDayOfWeek] = None
    reset_hour: Optional[int] = None
    complete_notification_namespace_id: Optional[str] = None
    anchor_timestamp: Optional[int] = None
    days: Optional[int] = None

    def __init__(
        self,
        name: str,
        reset_type: MissionGroupModelResetType,
        options: Optional[MissionGroupModelOptions] = MissionGroupModelOptions(),
    ):
        self.name = name
        self.reset_type = reset_type
        self.metadata = options.metadata if options.metadata else None
        self.tasks = options.tasks if options.tasks else None
        self.reset_day_of_month = options.reset_day_of_month if options.reset_day_of_month else None
        self.reset_day_of_week = options.reset_day_of_week if options.reset_day_of_week else None
        self.reset_hour = options.reset_hour if options.reset_hour else None
        self.complete_notification_namespace_id = options.complete_notification_namespace_id if options.complete_notification_namespace_id else None
        self.anchor_timestamp = options.anchor_timestamp if options.anchor_timestamp else None
        self.days = options.days if options.days else None

    @staticmethod
    def reset_type_is_not_reset(
        name: str,
        options: Optional[MissionGroupModelResetTypeIsNotResetOptions] = MissionGroupModelResetTypeIsNotResetOptions(),
    ) -> MissionGroupModel:
        return MissionGroupModel(
            name,
            MissionGroupModelResetType.NOT_RESET,
            MissionGroupModelOptions(
                options.metadata,
                options.tasks,
                options.complete_notification_namespace_id,
            ),
        )

    @staticmethod
    def reset_type_is_daily(
        name: str,
        reset_hour: int,
        options: Optional[MissionGroupModelResetTypeIsDailyOptions] = MissionGroupModelResetTypeIsDailyOptions(),
    ) -> MissionGroupModel:
        return MissionGroupModel(
            name,
            MissionGroupModelResetType.DAILY,
            MissionGroupModelOptions(
                reset_hour,
                options.metadata,
                options.tasks,
                options.complete_notification_namespace_id,
            ),
        )

    @staticmethod
    def reset_type_is_weekly(
        name: str,
        reset_day_of_week: MissionGroupModelResetDayOfWeek,
        reset_hour: int,
        options: Optional[MissionGroupModelResetTypeIsWeeklyOptions] = MissionGroupModelResetTypeIsWeeklyOptions(),
    ) -> MissionGroupModel:
        return MissionGroupModel(
            name,
            MissionGroupModelResetType.WEEKLY,
            MissionGroupModelOptions(
                reset_day_of_week,
                reset_hour,
                options.metadata,
                options.tasks,
                options.complete_notification_namespace_id,
            ),
        )

    @staticmethod
    def reset_type_is_monthly(
        name: str,
        reset_day_of_month: int,
        reset_hour: int,
        options: Optional[MissionGroupModelResetTypeIsMonthlyOptions] = MissionGroupModelResetTypeIsMonthlyOptions(),
    ) -> MissionGroupModel:
        return MissionGroupModel(
            name,
            MissionGroupModelResetType.MONTHLY,
            MissionGroupModelOptions(
                reset_day_of_month,
                reset_hour,
                options.metadata,
                options.tasks,
                options.complete_notification_namespace_id,
            ),
        )

    @staticmethod
    def reset_type_is_days(
        name: str,
        anchor_timestamp: int,
        days: int,
        options: Optional[MissionGroupModelResetTypeIsDaysOptions] = MissionGroupModelResetTypeIsDaysOptions(),
    ) -> MissionGroupModel:
        return MissionGroupModel(
            name,
            MissionGroupModelResetType.DAYS,
            MissionGroupModelOptions(
                anchor_timestamp,
                days,
                options.metadata,
                options.tasks,
                options.complete_notification_namespace_id,
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
        if self.tasks is not None:
            properties["tasks"] = [
                v.properties(
                )
                for v in self.tasks
            ]
        if self.reset_type is not None:
            properties["resetType"] = self.reset_type.value
        if self.reset_day_of_month is not None:
            properties["resetDayOfMonth"] = self.reset_day_of_month
        if self.reset_day_of_week is not None:
            properties["resetDayOfWeek"] = self.reset_day_of_week.value
        if self.reset_hour is not None:
            properties["resetHour"] = self.reset_hour
        if self.complete_notification_namespace_id is not None:
            properties["completeNotificationNamespaceId"] = self.complete_notification_namespace_id
        if self.anchor_timestamp is not None:
            properties["anchorTimestamp"] = self.anchor_timestamp
        if self.days is not None:
            properties["days"] = self.days

        return properties
