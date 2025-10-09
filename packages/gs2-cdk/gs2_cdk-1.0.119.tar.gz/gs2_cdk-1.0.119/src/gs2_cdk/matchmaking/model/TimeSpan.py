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
from .options.TimeSpanOptions import TimeSpanOptions


class TimeSpan:
    days: int
    hours: int
    minutes: int

    def __init__(
        self,
        days: int,
        hours: int,
        minutes: int,
        options: Optional[TimeSpanOptions] = TimeSpanOptions(),
    ):
        self.days = days
        self.hours = hours
        self.minutes = minutes

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.days is not None:
            properties["days"] = self.days
        if self.hours is not None:
            properties["hours"] = self.hours
        if self.minutes is not None:
            properties["minutes"] = self.minutes

        return properties
