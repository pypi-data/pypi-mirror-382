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
from .options.RepeatScheduleOptions import RepeatScheduleOptions


class RepeatSchedule:
    repeat_count: int
    current_repeat_start_at: Optional[int] = None
    current_repeat_end_at: Optional[int] = None
    last_repeat_end_at: Optional[int] = None
    next_repeat_start_at: Optional[int] = None

    def __init__(
        self,
        repeat_count: int,
        options: Optional[RepeatScheduleOptions] = RepeatScheduleOptions(),
    ):
        self.repeat_count = repeat_count
        self.current_repeat_start_at = options.current_repeat_start_at if options.current_repeat_start_at else None
        self.current_repeat_end_at = options.current_repeat_end_at if options.current_repeat_end_at else None
        self.last_repeat_end_at = options.last_repeat_end_at if options.last_repeat_end_at else None
        self.next_repeat_start_at = options.next_repeat_start_at if options.next_repeat_start_at else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.repeat_count is not None:
            properties["repeatCount"] = self.repeat_count
        if self.current_repeat_start_at is not None:
            properties["currentRepeatStartAt"] = self.current_repeat_start_at
        if self.current_repeat_end_at is not None:
            properties["currentRepeatEndAt"] = self.current_repeat_end_at
        if self.last_repeat_end_at is not None:
            properties["lastRepeatEndAt"] = self.last_repeat_end_at
        if self.next_repeat_start_at is not None:
            properties["nextRepeatStartAt"] = self.next_repeat_start_at

        return properties
