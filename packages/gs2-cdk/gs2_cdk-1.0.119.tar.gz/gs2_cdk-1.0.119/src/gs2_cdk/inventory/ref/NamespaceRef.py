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
from .InventoryModelRef import InventoryModelRef
from .SimpleInventoryModelRef import SimpleInventoryModelRef
from .BigInventoryModelRef import BigInventoryModelRef
from ..stamp_sheet.AddCapacityByUserId import AddCapacityByUserId
from ..stamp_sheet.SetCapacityByUserId import SetCapacityByUserId
from ..stamp_sheet.AcquireItemSetByUserId import AcquireItemSetByUserId
from ..stamp_sheet.AcquireItemSetWithGradeByUserId import AcquireItemSetWithGradeByUserId
from ..stamp_sheet.AddReferenceOfByUserId import AddReferenceOfByUserId
from ..stamp_sheet.DeleteReferenceOfByUserId import DeleteReferenceOfByUserId
from ..stamp_sheet.AcquireSimpleItemsByUserId import AcquireSimpleItemsByUserId
from ..model.AcquireCount import AcquireCount
from ..stamp_sheet.SetSimpleItemsByUserId import SetSimpleItemsByUserId
from ..stamp_sheet.AcquireBigItemByUserId import AcquireBigItemByUserId
from ..stamp_sheet.SetBigItemByUserId import SetBigItemByUserId
from ..stamp_sheet.ConsumeItemSetByUserId import ConsumeItemSetByUserId
from ..stamp_sheet.ConsumeSimpleItemsByUserId import ConsumeSimpleItemsByUserId
from ..stamp_sheet.ConsumeBigItemByUserId import ConsumeBigItemByUserId
from ..stamp_sheet.VerifyInventoryCurrentMaxCapacityByUserId import VerifyInventoryCurrentMaxCapacityByUserId
from ..stamp_sheet.VerifyItemSetByUserId import VerifyItemSetByUserId
from ..stamp_sheet.VerifyReferenceOfByUserId import VerifyReferenceOfByUserId
from ..stamp_sheet.VerifySimpleItemByUserId import VerifySimpleItemByUserId
from ..stamp_sheet.VerifyBigItemByUserId import VerifyBigItemByUserId


class NamespaceRef:
    namespace_name: str

    def __init__(
        self,
        namespace_name: str,
    ):
        self.namespace_name = namespace_name

    def inventory_model(
        self,
        inventory_name: str,
    ) -> InventoryModelRef:
        return InventoryModelRef(
            self.namespace_name,
            inventory_name,
        )

    def simple_inventory_model(
        self,
        inventory_name: str,
    ) -> SimpleInventoryModelRef:
        return SimpleInventoryModelRef(
            self.namespace_name,
            inventory_name,
        )

    def big_inventory_model(
        self,
        inventory_name: str,
    ) -> BigInventoryModelRef:
        return BigInventoryModelRef(
            self.namespace_name,
            inventory_name,
        )

    def add_capacity(
        self,
        inventory_name: str,
        add_capacity_value: int,
        user_id: Optional[str] = "#{userId}",
    ) -> AddCapacityByUserId:
        return AddCapacityByUserId(
            self.namespace_name,
            inventory_name,
            add_capacity_value,
            user_id,
        )

    def set_capacity(
        self,
        inventory_name: str,
        new_capacity_value: int,
        user_id: Optional[str] = "#{userId}",
    ) -> SetCapacityByUserId:
        return SetCapacityByUserId(
            self.namespace_name,
            inventory_name,
            new_capacity_value,
            user_id,
        )

    def acquire_item_set(
        self,
        inventory_name: str,
        item_name: str,
        acquire_count: int,
        expires_at: Optional[int] = None,
        create_new_item_set: Optional[bool] = None,
        item_set_name: Optional[str] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> AcquireItemSetByUserId:
        return AcquireItemSetByUserId(
            self.namespace_name,
            inventory_name,
            item_name,
            acquire_count,
            expires_at,
            create_new_item_set,
            item_set_name,
            user_id,
        )

    def acquire_item_set_with_grade(
        self,
        inventory_name: str,
        item_name: str,
        grade_model_id: str,
        grade_value: int,
        user_id: Optional[str] = "#{userId}",
    ) -> AcquireItemSetWithGradeByUserId:
        return AcquireItemSetWithGradeByUserId(
            self.namespace_name,
            inventory_name,
            item_name,
            grade_model_id,
            grade_value,
            user_id,
        )

    def add_reference_of(
        self,
        inventory_name: str,
        item_name: str,
        reference_of: str,
        item_set_name: Optional[str] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> AddReferenceOfByUserId:
        return AddReferenceOfByUserId(
            self.namespace_name,
            inventory_name,
            item_name,
            reference_of,
            item_set_name,
            user_id,
        )

    def delete_reference_of(
        self,
        inventory_name: str,
        item_name: str,
        reference_of: str,
        item_set_name: Optional[str] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> DeleteReferenceOfByUserId:
        return DeleteReferenceOfByUserId(
            self.namespace_name,
            inventory_name,
            item_name,
            reference_of,
            item_set_name,
            user_id,
        )

    def acquire_simple_items(
        self,
        inventory_name: str,
        acquire_counts: List[AcquireCount],
        user_id: Optional[str] = "#{userId}",
    ) -> AcquireSimpleItemsByUserId:
        return AcquireSimpleItemsByUserId(
            self.namespace_name,
            inventory_name,
            acquire_counts,
            user_id,
        )

    def set_simple_items(
        self,
        inventory_name: str,
        counts: List[HeldCount],
        user_id: Optional[str] = "#{userId}",
    ) -> SetSimpleItemsByUserId:
        return SetSimpleItemsByUserId(
            self.namespace_name,
            inventory_name,
            counts,
            user_id,
        )

    def acquire_big_item(
        self,
        inventory_name: str,
        item_name: str,
        acquire_count: str,
        user_id: Optional[str] = "#{userId}",
    ) -> AcquireBigItemByUserId:
        return AcquireBigItemByUserId(
            self.namespace_name,
            inventory_name,
            item_name,
            acquire_count,
            user_id,
        )

    def set_big_item(
        self,
        inventory_name: str,
        item_name: str,
        count: str,
        user_id: Optional[str] = "#{userId}",
    ) -> SetBigItemByUserId:
        return SetBigItemByUserId(
            self.namespace_name,
            inventory_name,
            item_name,
            count,
            user_id,
        )

    def consume_item_set(
        self,
        inventory_name: str,
        item_name: str,
        consume_count: int,
        item_set_name: Optional[str] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> ConsumeItemSetByUserId:
        return ConsumeItemSetByUserId(
            self.namespace_name,
            inventory_name,
            item_name,
            consume_count,
            item_set_name,
            user_id,
        )

    def consume_simple_items(
        self,
        inventory_name: str,
        consume_counts: List[ConsumeCount],
        user_id: Optional[str] = "#{userId}",
    ) -> ConsumeSimpleItemsByUserId:
        return ConsumeSimpleItemsByUserId(
            self.namespace_name,
            inventory_name,
            consume_counts,
            user_id,
        )

    def consume_big_item(
        self,
        inventory_name: str,
        item_name: str,
        consume_count: str,
        user_id: Optional[str] = "#{userId}",
    ) -> ConsumeBigItemByUserId:
        return ConsumeBigItemByUserId(
            self.namespace_name,
            inventory_name,
            item_name,
            consume_count,
            user_id,
        )

    def verify_inventory_current_max_capacity(
        self,
        inventory_name: str,
        verify_type: str,
        current_inventory_max_capacity: int,
        multiply_value_specifying_quantity: Optional[bool] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> VerifyInventoryCurrentMaxCapacityByUserId:
        return VerifyInventoryCurrentMaxCapacityByUserId(
            self.namespace_name,
            inventory_name,
            verify_type,
            current_inventory_max_capacity,
            multiply_value_specifying_quantity,
            user_id,
        )

    def verify_item_set(
        self,
        inventory_name: str,
        item_name: str,
        verify_type: str,
        count: int,
        item_set_name: Optional[str] = None,
        multiply_value_specifying_quantity: Optional[bool] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> VerifyItemSetByUserId:
        return VerifyItemSetByUserId(
            self.namespace_name,
            inventory_name,
            item_name,
            verify_type,
            count,
            item_set_name,
            multiply_value_specifying_quantity,
            user_id,
        )

    def verify_reference_of(
        self,
        inventory_name: str,
        item_name: str,
        reference_of: str,
        verify_type: str,
        item_set_name: Optional[str] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> VerifyReferenceOfByUserId:
        return VerifyReferenceOfByUserId(
            self.namespace_name,
            inventory_name,
            item_name,
            reference_of,
            verify_type,
            item_set_name,
            user_id,
        )

    def verify_simple_item(
        self,
        inventory_name: str,
        item_name: str,
        verify_type: str,
        count: int,
        multiply_value_specifying_quantity: Optional[bool] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> VerifySimpleItemByUserId:
        return VerifySimpleItemByUserId(
            self.namespace_name,
            inventory_name,
            item_name,
            verify_type,
            count,
            multiply_value_specifying_quantity,
            user_id,
        )

    def verify_big_item(
        self,
        inventory_name: str,
        item_name: str,
        verify_type: str,
        count: str,
        multiply_value_specifying_quantity: Optional[bool] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> VerifyBigItemByUserId:
        return VerifyBigItemByUserId(
            self.namespace_name,
            inventory_name,
            item_name,
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
            ],
        ).str(
        )
