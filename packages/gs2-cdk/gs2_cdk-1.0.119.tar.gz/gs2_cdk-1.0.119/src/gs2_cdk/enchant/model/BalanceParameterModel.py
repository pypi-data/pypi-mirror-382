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
from .BalanceParameterValueModel import BalanceParameterValueModel
from .options.BalanceParameterModelOptions import BalanceParameterModelOptions
from .enums.BalanceParameterModelInitialValueStrategy import BalanceParameterModelInitialValueStrategy


class BalanceParameterModel:
    name: str
    total_value: int
    initial_value_strategy: BalanceParameterModelInitialValueStrategy
    parameters: List[BalanceParameterValueModel]
    metadata: Optional[str] = None

    def __init__(
        self,
        name: str,
        total_value: int,
        initial_value_strategy: BalanceParameterModelInitialValueStrategy,
        parameters: List[BalanceParameterValueModel],
        options: Optional[BalanceParameterModelOptions] = BalanceParameterModelOptions(),
    ):
        self.name = name
        self.total_value = total_value
        self.initial_value_strategy = initial_value_strategy
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
        if self.total_value is not None:
            properties["totalValue"] = self.total_value
        if self.initial_value_strategy is not None:
            properties["initialValueStrategy"] = self.initial_value_strategy.value
        if self.parameters is not None:
            properties["parameters"] = [
                v.properties(
                )
                for v in self.parameters
            ]

        return properties
