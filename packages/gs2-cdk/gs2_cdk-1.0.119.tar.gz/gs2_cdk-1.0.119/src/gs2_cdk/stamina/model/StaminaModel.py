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
from .MaxStaminaTable import MaxStaminaTable
from .RecoverIntervalTable import RecoverIntervalTable
from .RecoverValueTable import RecoverValueTable
from .options.StaminaModelOptions import StaminaModelOptions


class StaminaModel:
    name: str
    recover_interval_minutes: int
    recover_value: int
    initial_capacity: int
    is_overflow: bool
    metadata: Optional[str] = None
    max_capacity: Optional[int] = None
    max_stamina_table: Optional[MaxStaminaTable] = None
    recover_interval_table: Optional[RecoverIntervalTable] = None
    recover_value_table: Optional[RecoverValueTable] = None

    def __init__(
        self,
        name: str,
        recover_interval_minutes: int,
        recover_value: int,
        initial_capacity: int,
        is_overflow: bool,
        options: Optional[StaminaModelOptions] = StaminaModelOptions(),
    ):
        self.name = name
        self.recover_interval_minutes = recover_interval_minutes
        self.recover_value = recover_value
        self.initial_capacity = initial_capacity
        self.is_overflow = is_overflow
        self.metadata = options.metadata if options.metadata else None
        self.max_capacity = options.max_capacity if options.max_capacity else None
        self.max_stamina_table = options.max_stamina_table if options.max_stamina_table else None
        self.recover_interval_table = options.recover_interval_table if options.recover_interval_table else None
        self.recover_value_table = options.recover_value_table if options.recover_value_table else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.name is not None:
            properties["name"] = self.name
        if self.metadata is not None:
            properties["metadata"] = self.metadata
        if self.recover_interval_minutes is not None:
            properties["recoverIntervalMinutes"] = self.recover_interval_minutes
        if self.recover_value is not None:
            properties["recoverValue"] = self.recover_value
        if self.initial_capacity is not None:
            properties["initialCapacity"] = self.initial_capacity
        if self.is_overflow is not None:
            properties["isOverflow"] = self.is_overflow
        if self.max_capacity is not None:
            properties["maxCapacity"] = self.max_capacity
        if self.max_stamina_table is not None:
            properties["maxStaminaTable"] = self.max_stamina_table.properties(
            )
        if self.recover_interval_table is not None:
            properties["recoverIntervalTable"] = self.recover_interval_table.properties(
            )
        if self.recover_value_table is not None:
            properties["recoverValueTable"] = self.recover_value_table.properties(
            )

        return properties
