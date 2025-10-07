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
from ..stamp_sheet.AcquireBigItemByUserId import AcquireBigItemByUserId
from ..stamp_sheet.SetBigItemByUserId import SetBigItemByUserId
from ..stamp_sheet.ConsumeBigItemByUserId import ConsumeBigItemByUserId
from ..stamp_sheet.VerifyBigItemByUserId import VerifyBigItemByUserId


class BigItemModelRef:
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

    def acquire_big_item(
        self,
        acquire_count: str,
        user_id: Optional[str] = "#{userId}",
    ) -> AcquireBigItemByUserId:
        return AcquireBigItemByUserId(
            self.namespace_name,
            self.inventory_name,
            self.item_name,
            acquire_count,
            user_id,
        )

    def set_big_item(
        self,
        count: str,
        user_id: Optional[str] = "#{userId}",
    ) -> SetBigItemByUserId:
        return SetBigItemByUserId(
            self.namespace_name,
            self.inventory_name,
            self.item_name,
            count,
            user_id,
        )

    def consume_big_item(
        self,
        consume_count: str,
        user_id: Optional[str] = "#{userId}",
    ) -> ConsumeBigItemByUserId:
        return ConsumeBigItemByUserId(
            self.namespace_name,
            self.inventory_name,
            self.item_name,
            consume_count,
            user_id,
        )

    def verify_big_item(
        self,
        verify_type: str,
        count: str,
        multiply_value_specifying_quantity: Optional[bool] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> VerifyBigItemByUserId:
        return VerifyBigItemByUserId(
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
                "big",
                "model",
                self.inventory_name,
                "item",
                self.item_name,
            ],
        ).str(
        )
