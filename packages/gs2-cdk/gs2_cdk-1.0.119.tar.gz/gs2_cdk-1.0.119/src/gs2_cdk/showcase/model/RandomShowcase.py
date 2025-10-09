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
from ...core.model import VerifyAction
from ...core.model import ConsumeAction
from ...core.model import AcquireAction
from .RandomDisplayItemModel import RandomDisplayItemModel
from .options.RandomShowcaseOptions import RandomShowcaseOptions


class RandomShowcase:
    name: str
    maximum_number_of_choice: int
    display_items: List[RandomDisplayItemModel]
    base_timestamp: int
    reset_interval_hours: int
    metadata: Optional[str] = None
    sales_period_event_id: Optional[str] = None

    def __init__(
        self,
        name: str,
        maximum_number_of_choice: int,
        display_items: List[RandomDisplayItemModel],
        base_timestamp: int,
        reset_interval_hours: int,
        options: Optional[RandomShowcaseOptions] = RandomShowcaseOptions(),
    ):
        self.name = name
        self.maximum_number_of_choice = maximum_number_of_choice
        self.display_items = display_items
        self.base_timestamp = base_timestamp
        self.reset_interval_hours = reset_interval_hours
        self.metadata = options.metadata if options.metadata else None
        self.sales_period_event_id = options.sales_period_event_id if options.sales_period_event_id else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.name is not None:
            properties["name"] = self.name
        if self.metadata is not None:
            properties["metadata"] = self.metadata
        if self.maximum_number_of_choice is not None:
            properties["maximumNumberOfChoice"] = self.maximum_number_of_choice
        if self.display_items is not None:
            properties["displayItems"] = [
                v.properties(
                )
                for v in self.display_items
            ]
        if self.base_timestamp is not None:
            properties["baseTimestamp"] = self.base_timestamp
        if self.reset_interval_hours is not None:
            properties["resetIntervalHours"] = self.reset_interval_hours
        if self.sales_period_event_id is not None:
            properties["salesPeriodEventId"] = self.sales_period_event_id

        return properties
