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
from .options.GradeEntryModelOptions import GradeEntryModelOptions


class GradeEntryModel:
    rank_cap_value: int
    property_id_regex: str
    grade_up_property_id_regex: str
    metadata: Optional[str] = None

    def __init__(
        self,
        rank_cap_value: int,
        property_id_regex: str,
        grade_up_property_id_regex: str,
        options: Optional[GradeEntryModelOptions] = GradeEntryModelOptions(),
    ):
        self.rank_cap_value = rank_cap_value
        self.property_id_regex = property_id_regex
        self.grade_up_property_id_regex = grade_up_property_id_regex
        self.metadata = options.metadata if options.metadata else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.metadata is not None:
            properties["metadata"] = self.metadata
        if self.rank_cap_value is not None:
            properties["rankCapValue"] = self.rank_cap_value
        if self.property_id_regex is not None:
            properties["propertyIdRegex"] = self.property_id_regex
        if self.grade_up_property_id_regex is not None:
            properties["gradeUpPropertyIdRegex"] = self.grade_up_property_id_regex

        return properties
