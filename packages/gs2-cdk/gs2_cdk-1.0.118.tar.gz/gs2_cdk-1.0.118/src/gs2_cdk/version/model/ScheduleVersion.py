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
from .Version import Version
from .options.ScheduleVersionOptions import ScheduleVersionOptions


class ScheduleVersion:
    current_version: Version
    warning_version: Version
    error_version: Version
    schedule_event_id: Optional[str] = None

    def __init__(
        self,
        current_version: Version,
        warning_version: Version,
        error_version: Version,
        options: Optional[ScheduleVersionOptions] = ScheduleVersionOptions(),
    ):
        self.current_version = current_version
        self.warning_version = warning_version
        self.error_version = error_version
        self.schedule_event_id = options.schedule_event_id if options.schedule_event_id else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.current_version is not None:
            properties["currentVersion"] = self.current_version.properties(
            )
        if self.warning_version is not None:
            properties["warningVersion"] = self.warning_version.properties(
            )
        if self.error_version is not None:
            properties["errorVersion"] = self.error_version.properties(
            )
        if self.schedule_event_id is not None:
            properties["scheduleEventId"] = self.schedule_event_id

        return properties
