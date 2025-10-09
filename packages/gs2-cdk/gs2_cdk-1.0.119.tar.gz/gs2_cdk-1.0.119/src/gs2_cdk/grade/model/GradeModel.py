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
from .DefaultGradeModel import DefaultGradeModel
from .GradeEntryModel import GradeEntryModel
from .AcquireActionRate import AcquireActionRate
from .options.GradeModelOptions import GradeModelOptions


class GradeModel:
    name: str
    experience_model_id: str
    grade_entries: List[GradeEntryModel]
    metadata: Optional[str] = None
    default_grades: Optional[List[DefaultGradeModel]] = None
    acquire_action_rates: Optional[List[AcquireActionRate]] = None

    def __init__(
        self,
        name: str,
        experience_model_id: str,
        grade_entries: List[GradeEntryModel],
        options: Optional[GradeModelOptions] = GradeModelOptions(),
    ):
        self.name = name
        self.experience_model_id = experience_model_id
        self.grade_entries = grade_entries
        self.metadata = options.metadata if options.metadata else None
        self.default_grades = options.default_grades if options.default_grades else None
        self.acquire_action_rates = options.acquire_action_rates if options.acquire_action_rates else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.name is not None:
            properties["name"] = self.name
        if self.metadata is not None:
            properties["metadata"] = self.metadata
        if self.default_grades is not None:
            properties["defaultGrades"] = [
                v.properties(
                )
                for v in self.default_grades
            ]
        if self.experience_model_id is not None:
            properties["experienceModelId"] = self.experience_model_id
        if self.grade_entries is not None:
            properties["gradeEntries"] = [
                v.properties(
                )
                for v in self.grade_entries
            ]
        if self.acquire_action_rates is not None:
            properties["acquireActionRates"] = [
                v.properties(
                )
                for v in self.acquire_action_rates
            ]

        return properties
