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
from .options.RepeatSettingOptions import RepeatSettingOptions
from .options.RepeatSettingRepeatTypeIsAlwaysOptions import RepeatSettingRepeatTypeIsAlwaysOptions
from .options.RepeatSettingRepeatTypeIsDailyOptions import RepeatSettingRepeatTypeIsDailyOptions
from .options.RepeatSettingRepeatTypeIsWeeklyOptions import RepeatSettingRepeatTypeIsWeeklyOptions
from .options.RepeatSettingRepeatTypeIsMonthlyOptions import RepeatSettingRepeatTypeIsMonthlyOptions
from .options.RepeatSettingRepeatTypeIsCustomOptions import RepeatSettingRepeatTypeIsCustomOptions
from .enums.RepeatSettingRepeatType import RepeatSettingRepeatType
from .enums.RepeatSettingBeginDayOfWeek import RepeatSettingBeginDayOfWeek
from .enums.RepeatSettingEndDayOfWeek import RepeatSettingEndDayOfWeek


class RepeatSetting:
    repeat_type: RepeatSettingRepeatType
    begin_day_of_month: Optional[int] = None
    end_day_of_month: Optional[int] = None
    begin_day_of_week: Optional[RepeatSettingBeginDayOfWeek] = None
    end_day_of_week: Optional[RepeatSettingEndDayOfWeek] = None
    begin_hour: Optional[int] = None
    end_hour: Optional[int] = None
    anchor_timestamp: Optional[int] = None
    active_days: Optional[int] = None
    inactive_days: Optional[int] = None

    def __init__(
        self,
        repeat_type: RepeatSettingRepeatType,
        options: Optional[RepeatSettingOptions] = RepeatSettingOptions(),
    ):
        self.repeat_type = repeat_type
        self.begin_day_of_month = options.begin_day_of_month if options.begin_day_of_month else None
        self.end_day_of_month = options.end_day_of_month if options.end_day_of_month else None
        self.begin_day_of_week = options.begin_day_of_week if options.begin_day_of_week else None
        self.end_day_of_week = options.end_day_of_week if options.end_day_of_week else None
        self.begin_hour = options.begin_hour if options.begin_hour else None
        self.end_hour = options.end_hour if options.end_hour else None
        self.anchor_timestamp = options.anchor_timestamp if options.anchor_timestamp else None
        self.active_days = options.active_days if options.active_days else None
        self.inactive_days = options.inactive_days if options.inactive_days else None

    @staticmethod
    def repeat_type_is_always(
        options: Optional[RepeatSettingRepeatTypeIsAlwaysOptions] = RepeatSettingRepeatTypeIsAlwaysOptions(),
    ) -> RepeatSetting:
        return RepeatSetting(
            RepeatSettingRepeatType.ALWAYS,
            RepeatSettingOptions(
            ),
        )

    @staticmethod
    def repeat_type_is_daily(
        begin_hour: int,
        end_hour: int,
        options: Optional[RepeatSettingRepeatTypeIsDailyOptions] = RepeatSettingRepeatTypeIsDailyOptions(),
    ) -> RepeatSetting:
        return RepeatSetting(
            RepeatSettingRepeatType.DAILY,
            RepeatSettingOptions(
                begin_hour,
                end_hour,
            ),
        )

    @staticmethod
    def repeat_type_is_weekly(
        begin_day_of_week: RepeatSettingBeginDayOfWeek,
        end_day_of_week: RepeatSettingEndDayOfWeek,
        begin_hour: int,
        end_hour: int,
        options: Optional[RepeatSettingRepeatTypeIsWeeklyOptions] = RepeatSettingRepeatTypeIsWeeklyOptions(),
    ) -> RepeatSetting:
        return RepeatSetting(
            RepeatSettingRepeatType.WEEKLY,
            RepeatSettingOptions(
                begin_day_of_week,
                end_day_of_week,
                begin_hour,
                end_hour,
            ),
        )

    @staticmethod
    def repeat_type_is_monthly(
        begin_day_of_month: int,
        end_day_of_month: int,
        begin_hour: int,
        end_hour: int,
        options: Optional[RepeatSettingRepeatTypeIsMonthlyOptions] = RepeatSettingRepeatTypeIsMonthlyOptions(),
    ) -> RepeatSetting:
        return RepeatSetting(
            RepeatSettingRepeatType.MONTHLY,
            RepeatSettingOptions(
                begin_day_of_month,
                end_day_of_month,
                begin_hour,
                end_hour,
            ),
        )

    @staticmethod
    def repeat_type_is_custom(
        anchor_timestamp: int,
        active_days: int,
        inactive_days: int,
        options: Optional[RepeatSettingRepeatTypeIsCustomOptions] = RepeatSettingRepeatTypeIsCustomOptions(),
    ) -> RepeatSetting:
        return RepeatSetting(
            RepeatSettingRepeatType.CUSTOM,
            RepeatSettingOptions(
                anchor_timestamp,
                active_days,
                inactive_days,
            ),
        )

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.repeat_type is not None:
            properties["repeatType"] = self.repeat_type.value
        if self.begin_day_of_month is not None:
            properties["beginDayOfMonth"] = self.begin_day_of_month
        if self.end_day_of_month is not None:
            properties["endDayOfMonth"] = self.end_day_of_month
        if self.begin_day_of_week is not None:
            properties["beginDayOfWeek"] = self.begin_day_of_week.value
        if self.end_day_of_week is not None:
            properties["endDayOfWeek"] = self.end_day_of_week.value
        if self.begin_hour is not None:
            properties["beginHour"] = self.begin_hour
        if self.end_hour is not None:
            properties["endHour"] = self.end_hour
        if self.anchor_timestamp is not None:
            properties["anchorTimestamp"] = self.anchor_timestamp
        if self.active_days is not None:
            properties["activeDays"] = self.active_days
        if self.inactive_days is not None:
            properties["inactiveDays"] = self.inactive_days

        return properties
