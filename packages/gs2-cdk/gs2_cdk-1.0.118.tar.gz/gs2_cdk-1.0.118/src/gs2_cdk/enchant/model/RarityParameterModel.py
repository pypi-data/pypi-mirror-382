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
from .RarityParameterCountModel import RarityParameterCountModel
from .RarityParameterValueModel import RarityParameterValueModel
from .options.RarityParameterModelOptions import RarityParameterModelOptions


class RarityParameterModel:
    name: str
    maximum_parameter_count: int
    parameter_counts: List[RarityParameterCountModel]
    parameters: List[RarityParameterValueModel]
    metadata: Optional[str] = None

    def __init__(
        self,
        name: str,
        maximum_parameter_count: int,
        parameter_counts: List[RarityParameterCountModel],
        parameters: List[RarityParameterValueModel],
        options: Optional[RarityParameterModelOptions] = RarityParameterModelOptions(),
    ):
        self.name = name
        self.maximum_parameter_count = maximum_parameter_count
        self.parameter_counts = parameter_counts
        self.parameters = parameters
        self.metadata = options.metadata if options.metadata else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.name is not None:
            properties["name"] = self.name
        if self.metadata is not None:
            properties["metadata"] = self.metadata
        if self.maximum_parameter_count is not None:
            properties["maximumParameterCount"] = self.maximum_parameter_count
        if self.parameter_counts is not None:
            properties["parameterCounts"] = [
                v.properties(
                )
                for v in self.parameter_counts
            ]
        if self.parameters is not None:
            properties["parameters"] = [
                v.properties(
                )
                for v in self.parameters
            ]

        return properties
