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

from ...core.func import GetAttr, Join
from ..stamp_sheet.AcquireSimpleItemsByUserId import AcquireSimpleItemsByUserId
from ..model.AcquireCount import AcquireCount
from ..stamp_sheet.SetSimpleItemsByUserId import SetSimpleItemsByUserId
from ..stamp_sheet.ConsumeSimpleItemsByUserId import ConsumeSimpleItemsByUserId
from ..stamp_sheet.VerifySimpleItemByUserId import VerifySimpleItemByUserId


class SimpleItemModelRef:
    namespace_name: str
    inventory_name: str
    item_name: str

    def __init__(
        self,
        namespace_name: str,
        inventory_name: str,
        item_name: str,
    ):
        self.namespace_name = namespace_name
        self.inventory_name = inventory_name
        self.item_name = item_name

    def acquire_simple_items(
        self,
        acquire_counts: List[AcquireCount],
        user_id: Optional[str] = "#{userId}",
    ) -> AcquireSimpleItemsByUserId:
        return AcquireSimpleItemsByUserId(
            self.namespace_name,
            self.inventory_name,
            acquire_counts,
            user_id,
        )

    def set_simple_items(
        self,
        counts: List[HeldCount],
        user_id: Optional[str] = "#{userId}",
    ) -> SetSimpleItemsByUserId:
        return SetSimpleItemsByUserId(
            self.namespace_name,
            self.inventory_name,
            counts,
            user_id,
        )

    def consume_simple_items(
        self,
        consume_counts: List[ConsumeCount],
        user_id: Optional[str] = "#{userId}",
    ) -> ConsumeSimpleItemsByUserId:
        return ConsumeSimpleItemsByUserId(
            self.namespace_name,
            self.inventory_name,
            consume_counts,
            user_id,
        )

    def verify_simple_item(
        self,
        verify_type: str,
        count: int,
        multiply_value_specifying_quantity: Optional[bool] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> VerifySimpleItemByUserId:
        return VerifySimpleItemByUserId(
            self.namespace_name,
            self.inventory_name,
            self.item_name,
            verify_type,
            count,
            multiply_value_specifying_quantity,
            user_id,
        )

    def grn(
        self,
    ) -> str:
        return Join(
            ":",
            [
                "grn",
                "gs2",
                GetAttr.region(
                ).str(
                ),
                GetAttr.owner_id(
                ).str(
                ),
                "inventory",
                self.namespace_name,
                "simple",
                "model",
                self.inventory_name,
                "item",
                self.item_name,
            ],
        ).str(
        )
