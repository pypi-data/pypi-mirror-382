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
from .RepeatSetting import RepeatSetting
from .options.EventOptions import EventOptions
from .options.EventScheduleTypeIsAbsoluteOptions import EventScheduleTypeIsAbsoluteOptions
from .options.EventScheduleTypeIsRelativeOptions import EventScheduleTypeIsRelativeOptions
from .options.EventRepeatTypeIsAlwaysOptions import EventRepeatTypeIsAlwaysOptions
from .options.EventRepeatTypeIsDailyOptions import EventRepeatTypeIsDailyOptions
from .options.EventRepeatTypeIsWeeklyOptions import EventRepeatTypeIsWeeklyOptions
from .options.EventRepeatTypeIsMonthlyOptions import EventRepeatTypeIsMonthlyOptions
from .enums.EventScheduleType import EventScheduleType
from .enums.EventRepeatType import EventRepeatType
from .enums.EventRepeatBeginDayOfWeek import EventRepeatBeginDayOfWeek
from .enums.EventRepeatEndDayOfWeek import EventRepeatEndDayOfWeek


class Event:
    name: str
    schedule_type: EventScheduleType
    repeat_setting: RepeatSetting
    repeat_type: EventRepeatType
    metadata: Optional[str] = None
    absolute_begin: Optional[int] = None
    absolute_end: Optional[int] = None
    relative_trigger_name: Optional[str] = None
    repeat_begin_day_of_month: Optional[int] = None
    repeat_end_day_of_month: Optional[int] = None
    repeat_begin_day_of_week: Optional[EventRepeatBeginDayOfWeek] = None
    repeat_end_day_of_week: Optional[EventRepeatEndDayOfWeek] = None
    repeat_begin_hour: Optional[int] = None
    repeat_end_hour: Optional[int] = None

    def __init__(
        self,
        name: str,
        schedule_type: EventScheduleType,
        repeat_setting: RepeatSetting,
        options: Optional[EventOptions] = EventOptions(),
    ):
        self.name = name
        self.schedule_type = schedule_type
        self.repeat_setting = repeat_setting
        self.repeat_type = options.repeat_type if options.repeat_type else None
        self.metadata = options.metadata if options.metadata else None
        self.absolute_begin = options.absolute_begin if options.absolute_begin else None
        self.absolute_end = options.absolute_end if options.absolute_end else None
        self.relative_trigger_name = options.relative_trigger_name if options.relative_trigger_name else None
        self.repeat_begin_day_of_month = options.repeat_begin_day_of_month if options.repeat_begin_day_of_month else None
        self.repeat_end_day_of_month = options.repeat_end_day_of_month if options.repeat_end_day_of_month else None
        self.repeat_begin_day_of_week = options.repeat_begin_day_of_week if options.repeat_begin_day_of_week else None
        self.repeat_end_day_of_week = options.repeat_end_day_of_week if options.repeat_end_day_of_week else None
        self.repeat_begin_hour = options.repeat_begin_hour if options.repeat_begin_hour else None
        self.repeat_end_hour = options.repeat_end_hour if options.repeat_end_hour else None

    @staticmethod
    def schedule_type_is_absolute(
        name: str,
        repeat_setting: RepeatSetting,
        options: Optional[EventScheduleTypeIsAbsoluteOptions] = EventScheduleTypeIsAbsoluteOptions(),
    ) -> Event:
        return Event(
            name,
            EventScheduleType.ABSOLUTE,
            repeat_setting,
            EventOptions(
                options.metadata,
                options.absolute_begin,
                options.absolute_end,
            ),
        )

    @staticmethod
    def schedule_type_is_relative(
        name: str,
        repeat_setting: RepeatSetting,
        relative_trigger_name: str,
        options: Optional[EventScheduleTypeIsRelativeOptions] = EventScheduleTypeIsRelativeOptions(),
    ) -> Event:
        return Event(
            name,
            EventScheduleType.RELATIVE,
            repeat_setting,
            EventOptions(
                metadata = options.metadata,
                absolute_begin = options.absolute_begin,
                absolute_end = options.absolute_end,
                relative_trigger_name = relative_trigger_name,
            ),
        )

    @staticmethod
    def repeat_type_is_always(
        name: str,
        schedule_type: EventScheduleType,
        repeat_setting: RepeatSetting,
        options: Optional[EventRepeatTypeIsAlwaysOptions] = EventRepeatTypeIsAlwaysOptions(),
    ) -> Event:
        return Event(
            name,
            schedule_type,
            repeat_setting,
            EventOptions(
                EventRepeatType.ALWAYS,
                options.metadata,
                options.absolute_begin,
                options.absolute_end,
            ),
        )

    @staticmethod
    def repeat_type_is_daily(
        name: str,
        schedule_type: EventScheduleType,
        repeat_setting: RepeatSetting,
        repeat_begin_hour: int,
        repeat_end_hour: int,
        options: Optional[EventRepeatTypeIsDailyOptions] = EventRepeatTypeIsDailyOptions(),
    ) -> Event:
        return Event(
            name,
            schedule_type,
            repeat_setting,
            EventOptions(
                repeat_type = EventRepeatType.DAILY,
                repeat_begin_hour = repeat_begin_hour,
                repeat_end_hour = repeat_end_hour,
                metadata = options.metadata,
                absolute_begin = options.absolute_begin,
                absolute_end = options.absolute_end,
            ),
        )

    @staticmethod
    def repeat_type_is_weekly(
        name: str,
        schedule_type: EventScheduleType,
        repeat_setting: RepeatSetting,
        repeat_begin_day_of_week: EventRepeatBeginDayOfWeek,
        repeat_end_day_of_week: EventRepeatEndDayOfWeek,
        repeat_begin_hour: int,
        repeat_end_hour: int,
        options: Optional[EventRepeatTypeIsWeeklyOptions] = EventRepeatTypeIsWeeklyOptions(),
    ) -> Event:
        return Event(
            name,
            schedule_type,
            repeat_setting,
            EventOptions(
                repeat_type = EventRepeatType.WEEKLY,
                repeat_begin_day_of_week = repeat_begin_day_of_week,
                repeat_end_day_of_week = repeat_end_day_of_week,
                repeat_begin_hour = repeat_begin_hour,
                repeat_end_hour = repeat_end_hour,
                metadata = options.metadata,
                absolute_begin = options.absolute_begin,
                absolute_end = options.absolute_end,
            ),
        )

    @staticmethod
    def repeat_type_is_monthly(
        name: str,
        schedule_type: EventScheduleType,
        repeat_setting: RepeatSetting,
        repeat_begin_day_of_month: int,
        repeat_end_day_of_month: int,
        repeat_begin_hour: int,
        repeat_end_hour: int,
        options: Optional[EventRepeatTypeIsMonthlyOptions] = EventRepeatTypeIsMonthlyOptions(),
    ) -> Event:
        return Event(
            name,
            schedule_type,
            repeat_setting,
            EventOptions(
                repeat_type = EventRepeatType.MONTHLY,
                repeat_begin_day_of_month = repeat_begin_day_of_month,
                repeat_end_day_of_month = repeat_end_day_of_month,
                repeat_begin_hour = repeat_begin_hour,
                repeat_end_hour = repeat_end_hour,
                metadata = options.metadata,
                absolute_begin = options.absolute_begin,
                absolute_end = options.absolute_end,
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
        if self.schedule_type is not None:
            properties["scheduleType"] = self.schedule_type.value
        if self.absolute_begin is not None:
            properties["absoluteBegin"] = self.absolute_begin
        if self.absolute_end is not None:
            properties["absoluteEnd"] = self.absolute_end
        if self.relative_trigger_name is not None:
            properties["relativeTriggerName"] = self.relative_trigger_name
        if self.repeat_setting is not None:
            properties["repeatSetting"] = self.repeat_setting.properties(
            )
        if self.repeat_type is not None:
            properties["repeatType"] = self.repeat_type.value
        if self.repeat_begin_day_of_month is not None:
            properties["repeatBeginDayOfMonth"] = self.repeat_begin_day_of_month
        if self.repeat_end_day_of_month is not None:
            properties["repeatEndDayOfMonth"] = self.repeat_end_day_of_month
        if self.repeat_begin_day_of_week is not None:
            properties["repeatBeginDayOfWeek"] = self.repeat_begin_day_of_week.value
        if self.repeat_end_day_of_week is not None:
            properties["repeatEndDayOfWeek"] = self.repeat_end_day_of_week.value
        if self.repeat_begin_hour is not None:
            properties["repeatBeginHour"] = self.repeat_begin_hour
        if self.repeat_end_hour is not None:
            properties["repeatEndHour"] = self.repeat_end_hour

        return properties
