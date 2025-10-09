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
from .options.DefaultGradeModelOptions import DefaultGradeModelOptions


class DefaultGradeModel:
    property_id_regex: str
    default_grade_value: int

    def __init__(
        self,
        property_id_regex: str,
        default_grade_value: int,
        options: Optional[DefaultGradeModelOptions] = DefaultGradeModelOptions(),
    ):
        self.property_id_regex = property_id_regex
        self.default_grade_value = default_grade_value

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.property_id_regex is not None:
            properties["propertyIdRegex"] = self.property_id_regex
        if self.default_grade_value is not None:
            properties["defaultGradeValue"] = self.default_grade_value

        return properties
