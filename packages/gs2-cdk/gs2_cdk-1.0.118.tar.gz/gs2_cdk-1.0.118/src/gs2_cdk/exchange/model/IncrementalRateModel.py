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
from ...core.model import ConsumeAction
from ...core.model import AcquireAction
from .options.IncrementalRateModelOptions import IncrementalRateModelOptions
from .options.IncrementalRateModelCalculateTypeIsLinearOptions import IncrementalRateModelCalculateTypeIsLinearOptions
from .options.IncrementalRateModelCalculateTypeIsPowerOptions import IncrementalRateModelCalculateTypeIsPowerOptions
from .options.IncrementalRateModelCalculateTypeIsGs2ScriptOptions import IncrementalRateModelCalculateTypeIsGs2ScriptOptions
from .enums.IncrementalRateModelCalculateType import IncrementalRateModelCalculateType


class IncrementalRateModel:
    name: str
    consume_action: ConsumeAction
    calculate_type: IncrementalRateModelCalculateType
    exchange_count_id: str
    maximum_exchange_count: int
    metadata: Optional[str] = None
    base_value: Optional[int] = None
    coefficient_value: Optional[int] = None
    calculate_script_id: Optional[str] = None
    acquire_actions: Optional[List[AcquireAction]] = None

    def __init__(
        self,
        name: str,
        consume_action: ConsumeAction,
        calculate_type: IncrementalRateModelCalculateType,
        exchange_count_id: str,
        maximum_exchange_count: int,
        options: Optional[IncrementalRateModelOptions] = IncrementalRateModelOptions(),
    ):
        self.name = name
        self.consume_action = consume_action
        self.calculate_type = calculate_type
        self.exchange_count_id = exchange_count_id
        self.maximum_exchange_count = maximum_exchange_count
        self.metadata = options.metadata if options.metadata else None
        self.base_value = options.base_value if options.base_value else None
        self.coefficient_value = options.coefficient_value if options.coefficient_value else None
        self.calculate_script_id = options.calculate_script_id if options.calculate_script_id else None
        self.acquire_actions = options.acquire_actions if options.acquire_actions else None

    @staticmethod
    def calculate_type_is_linear(
        name: str,
        consume_action: ConsumeAction,
        exchange_count_id: str,
        maximum_exchange_count: int,
        base_value: int,
        coefficient_value: int,
        options: Optional[IncrementalRateModelCalculateTypeIsLinearOptions] = IncrementalRateModelCalculateTypeIsLinearOptions(),
    ) -> IncrementalRateModel:
        return IncrementalRateModel(
            name,
            consume_action,
            IncrementalRateModelCalculateType.LINEAR,
            exchange_count_id,
            maximum_exchange_count,
            IncrementalRateModelOptions(
                base_value,
                coefficient_value,
                options.metadata,
                options.acquire_actions,
            ),
        )

    @staticmethod
    def calculate_type_is_power(
        name: str,
        consume_action: ConsumeAction,
        exchange_count_id: str,
        maximum_exchange_count: int,
        coefficient_value: int,
        options: Optional[IncrementalRateModelCalculateTypeIsPowerOptions] = IncrementalRateModelCalculateTypeIsPowerOptions(),
    ) -> IncrementalRateModel:
        return IncrementalRateModel(
            name,
            consume_action,
            IncrementalRateModelCalculateType.POWER,
            exchange_count_id,
            maximum_exchange_count,
            IncrementalRateModelOptions(
                coefficient_value,
                options.metadata,
                options.acquire_actions,
            ),
        )

    @staticmethod
    def calculate_type_is_gs2_script(
        name: str,
        consume_action: ConsumeAction,
        exchange_count_id: str,
        maximum_exchange_count: int,
        calculate_script_id: str,
        options: Optional[IncrementalRateModelCalculateTypeIsGs2ScriptOptions] = IncrementalRateModelCalculateTypeIsGs2ScriptOptions(),
    ) -> IncrementalRateModel:
        return IncrementalRateModel(
            name,
            consume_action,
            IncrementalRateModelCalculateType.GS2_SCRIPT,
            exchange_count_id,
            maximum_exchange_count,
            IncrementalRateModelOptions(
                calculate_script_id,
                options.metadata,
                options.acquire_actions,
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
        if self.consume_action is not None:
            properties["consumeAction"] = self.consume_action.properties(
            )
        if self.calculate_type is not None:
            properties["calculateType"] = self.calculate_type.value
        if self.base_value is not None:
            properties["baseValue"] = self.base_value
        if self.coefficient_value is not None:
            properties["coefficientValue"] = self.coefficient_value
        if self.calculate_script_id is not None:
            properties["calculateScriptId"] = self.calculate_script_id
        if self.exchange_count_id is not None:
            properties["exchangeCountId"] = self.exchange_count_id
        if self.maximum_exchange_count is not None:
            properties["maximumExchangeCount"] = self.maximum_exchange_count
        if self.acquire_actions is not None:
            properties["acquireActions"] = [
                v.properties(
                )
                for v in self.acquire_actions
            ]

        return properties
