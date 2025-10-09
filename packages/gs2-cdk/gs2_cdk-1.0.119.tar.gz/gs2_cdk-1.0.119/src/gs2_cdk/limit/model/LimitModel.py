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
from .options.LimitModelOptions import LimitModelOptions
from .options.LimitModelResetTypeIsNotResetOptions import LimitModelResetTypeIsNotResetOptions
from .options.LimitModelResetTypeIsDailyOptions import LimitModelResetTypeIsDailyOptions
from .options.LimitModelResetTypeIsWeeklyOptions import LimitModelResetTypeIsWeeklyOptions
from .options.LimitModelResetTypeIsMonthlyOptions import LimitModelResetTypeIsMonthlyOptions
from .options.LimitModelResetTypeIsDaysOptions import LimitModelResetTypeIsDaysOptions
from .enums.LimitModelResetType import LimitModelResetType
from .enums.LimitModelResetDayOfWeek import LimitModelResetDayOfWeek


class LimitModel:
    name: str
    reset_type: LimitModelResetType
    metadata: Optional[str] = None
    reset_day_of_month: Optional[int] = None
    reset_day_of_week: Optional[LimitModelResetDayOfWeek] = None
    reset_hour: Optional[int] = None
    anchor_timestamp: Optional[int] = None
    days: Optional[int] = None

    def __init__(
        self,
        name: str,
        reset_type: LimitModelResetType,
        options: Optional[LimitModelOptions] = LimitModelOptions(),
    ):
        self.name = name
        self.reset_type = reset_type
        self.metadata = options.metadata if options.metadata else None
        self.reset_day_of_month = options.reset_day_of_month if options.reset_day_of_month else None
        self.reset_day_of_week = options.reset_day_of_week if options.reset_day_of_week else None
        self.reset_hour = options.reset_hour if options.reset_hour else None
        self.anchor_timestamp = options.anchor_timestamp if options.anchor_timestamp else None
        self.days = options.days if options.days else None

    @staticmethod
    def reset_type_is_not_reset(
        name: str,
        options: Optional[LimitModelResetTypeIsNotResetOptions] = LimitModelResetTypeIsNotResetOptions(),
    ) -> LimitModel:
        return LimitModel(
            name,
            LimitModelResetType.NOT_RESET,
            LimitModelOptions(
                options.metadata,
            ),
        )

    @staticmethod
    def reset_type_is_daily(
        name: str,
        reset_hour: int,
        options: Optional[LimitModelResetTypeIsDailyOptions] = LimitModelResetTypeIsDailyOptions(),
    ) -> LimitModel:
        return LimitModel(
            name,
            LimitModelResetType.DAILY,
            LimitModelOptions(
                reset_hour,
                options.metadata,
            ),
        )

    @staticmethod
    def reset_type_is_weekly(
        name: str,
        reset_day_of_week: LimitModelResetDayOfWeek,
        reset_hour: int,
        options: Optional[LimitModelResetTypeIsWeeklyOptions] = LimitModelResetTypeIsWeeklyOptions(),
    ) -> LimitModel:
        return LimitModel(
            name,
            LimitModelResetType.WEEKLY,
            LimitModelOptions(
                reset_day_of_week,
                reset_hour,
                options.metadata,
            ),
        )

    @staticmethod
    def reset_type_is_monthly(
        name: str,
        reset_day_of_month: int,
        reset_hour: int,
        options: Optional[LimitModelResetTypeIsMonthlyOptions] = LimitModelResetTypeIsMonthlyOptions(),
    ) -> LimitModel:
        return LimitModel(
            name,
            LimitModelResetType.MONTHLY,
            LimitModelOptions(
                reset_day_of_month,
                reset_hour,
                options.metadata,
            ),
        )

    @staticmethod
    def reset_type_is_days(
        name: str,
        anchor_timestamp: int,
        days: int,
        options: Optional[LimitModelResetTypeIsDaysOptions] = LimitModelResetTypeIsDaysOptions(),
    ) -> LimitModel:
        return LimitModel(
            name,
            LimitModelResetType.DAYS,
            LimitModelOptions(
                anchor_timestamp,
                days,
                options.metadata,
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
        if self.reset_type is not None:
            properties["resetType"] = self.reset_type.value
        if self.reset_day_of_month is not None:
            properties["resetDayOfMonth"] = self.reset_day_of_month
        if self.reset_day_of_week is not None:
            properties["resetDayOfWeek"] = self.reset_day_of_week.value
        if self.reset_hour is not None:
            properties["resetHour"] = self.reset_hour
        if self.anchor_timestamp is not None:
            properties["anchorTimestamp"] = self.anchor_timestamp
        if self.days is not None:
            properties["days"] = self.days

        return properties
