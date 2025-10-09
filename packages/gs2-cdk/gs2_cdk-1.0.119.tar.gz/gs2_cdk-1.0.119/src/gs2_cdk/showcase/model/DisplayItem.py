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
from .SalesItem import SalesItem
from .SalesItemGroup import SalesItemGroup
from .options.DisplayItemOptions import DisplayItemOptions
from .options.DisplayItemTypeIsSalesItemOptions import DisplayItemTypeIsSalesItemOptions
from .options.DisplayItemTypeIsSalesItemGroupOptions import DisplayItemTypeIsSalesItemGroupOptions
from .enums.DisplayItemType import DisplayItemType


class DisplayItem:
    display_item_id: str
    type: DisplayItemType
    sales_item: Optional[SalesItem] = None
    sales_item_group: Optional[SalesItemGroup] = None
    sales_period_event_id: Optional[str] = None

    def __init__(
        self,
        display_item_id: str,
        type: DisplayItemType,
        options: Optional[DisplayItemOptions] = DisplayItemOptions(),
    ):
        self.display_item_id = display_item_id
        self.type = type
        self.sales_item = options.sales_item if options.sales_item else None
        self.sales_item_group = options.sales_item_group if options.sales_item_group else None
        self.sales_period_event_id = options.sales_period_event_id if options.sales_period_event_id else None

    @staticmethod
    def type_is_sales_item(
        display_item_id: str,
        sales_item: SalesItem,
        options: Optional[DisplayItemTypeIsSalesItemOptions] = DisplayItemTypeIsSalesItemOptions(),
    ) -> DisplayItem:
        return DisplayItem(
            display_item_id,
            DisplayItemType.SALES_ITEM,
            DisplayItemOptions(
                sales_item,
                options.sales_period_event_id,
            ),
        )

    @staticmethod
    def type_is_sales_item_group(
        display_item_id: str,
        sales_item_group: SalesItemGroup,
        options: Optional[DisplayItemTypeIsSalesItemGroupOptions] = DisplayItemTypeIsSalesItemGroupOptions(),
    ) -> DisplayItem:
        return DisplayItem(
            display_item_id,
            DisplayItemType.SALES_ITEM_GROUP,
            DisplayItemOptions(
                sales_item_group,
                options.sales_period_event_id,
            ),
        )

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.display_item_id is not None:
            properties["displayItemId"] = self.display_item_id
        if self.type is not None:
            properties["type"] = self.type.value
        if self.sales_item is not None:
            properties["salesItem"] = self.sales_item.properties(
            )
        if self.sales_item_group is not None:
            properties["salesItemGroup"] = self.sales_item_group.properties(
            )
        if self.sales_period_event_id is not None:
            properties["salesPeriodEventId"] = self.sales_period_event_id

        return properties
