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
from .options.SubscribeRankingModelOptions import SubscribeRankingModelOptions
from .enums.SubscribeRankingModelOrderDirection import SubscribeRankingModelOrderDirection


class SubscribeRankingModel:
    name: str
    sum: bool
    order_direction: SubscribeRankingModelOrderDirection
    metadata: Optional[str] = None
    minimum_value: Optional[int] = None
    maximum_value: Optional[int] = None
    entry_period_event_id: Optional[str] = None
    access_period_event_id: Optional[str] = None

    def __init__(
        self,
        name: str,
        sum: bool,
        order_direction: SubscribeRankingModelOrderDirection,
        options: Optional[SubscribeRankingModelOptions] = SubscribeRankingModelOptions(),
    ):
        self.name = name
        self.sum = sum
        self.order_direction = order_direction
        self.metadata = options.metadata if options.metadata else None
        self.minimum_value = options.minimum_value if options.minimum_value else None
        self.maximum_value = options.maximum_value if options.maximum_value else None
        self.entry_period_event_id = options.entry_period_event_id if options.entry_period_event_id else None
        self.access_period_event_id = options.access_period_event_id if options.access_period_event_id else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.name is not None:
            properties["name"] = self.name
        if self.metadata is not None:
            properties["metadata"] = self.metadata
        if self.minimum_value is not None:
            properties["minimumValue"] = self.minimum_value
        if self.maximum_value is not None:
            properties["maximumValue"] = self.maximum_value
        if self.sum is not None:
            properties["sum"] = self.sum
        if self.order_direction is not None:
            properties["orderDirection"] = self.order_direction.value
        if self.entry_period_event_id is not None:
            properties["entryPeriodEventId"] = self.entry_period_event_id
        if self.access_period_event_id is not None:
            properties["accessPeriodEventId"] = self.access_period_event_id

        return properties
