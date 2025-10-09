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
from ..stamp_sheet.AcquireItemSetByUserId import AcquireItemSetByUserId
from ..stamp_sheet.AcquireItemSetWithGradeByUserId import AcquireItemSetWithGradeByUserId
from ..stamp_sheet.AddReferenceOfByUserId import AddReferenceOfByUserId
from ..stamp_sheet.DeleteReferenceOfByUserId import DeleteReferenceOfByUserId
from ..stamp_sheet.ConsumeItemSetByUserId import ConsumeItemSetByUserId
from ..stamp_sheet.VerifyItemSetByUserId import VerifyItemSetByUserId
from ..stamp_sheet.VerifyReferenceOfByUserId import VerifyReferenceOfByUserId


class ItemModelRef:
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

    def acquire_item_set(
        self,
        acquire_count: int,
        expires_at: Optional[int] = None,
        create_new_item_set: Optional[bool] = None,
        item_set_name: Optional[str] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> AcquireItemSetByUserId:
        return AcquireItemSetByUserId(
            self.namespace_name,
            self.inventory_name,
            self.item_name,
            acquire_count,
            expires_at,
            create_new_item_set,
            item_set_name,
            user_id,
        )

    def acquire_item_set_with_grade(
        self,
        grade_model_id: str,
        grade_value: int,
        user_id: Optional[str] = "#{userId}",
    ) -> AcquireItemSetWithGradeByUserId:
        return AcquireItemSetWithGradeByUserId(
            self.namespace_name,
            self.inventory_name,
            self.item_name,
            grade_model_id,
            grade_value,
            user_id,
        )

    def add_reference_of(
        self,
        reference_of: str,
        item_set_name: Optional[str] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> AddReferenceOfByUserId:
        return AddReferenceOfByUserId(
            self.namespace_name,
            self.inventory_name,
            self.item_name,
            reference_of,
            item_set_name,
            user_id,
        )

    def delete_reference_of(
        self,
        reference_of: str,
        item_set_name: Optional[str] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> DeleteReferenceOfByUserId:
        return DeleteReferenceOfByUserId(
            self.namespace_name,
            self.inventory_name,
            self.item_name,
            reference_of,
            item_set_name,
            user_id,
        )

    def consume_item_set(
        self,
        consume_count: int,
        item_set_name: Optional[str] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> ConsumeItemSetByUserId:
        return ConsumeItemSetByUserId(
            self.namespace_name,
            self.inventory_name,
            self.item_name,
            consume_count,
            item_set_name,
            user_id,
        )

    def verify_item_set(
        self,
        verify_type: str,
        count: int,
        item_set_name: Optional[str] = None,
        multiply_value_specifying_quantity: Optional[bool] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> VerifyItemSetByUserId:
        return VerifyItemSetByUserId(
            self.namespace_name,
            self.inventory_name,
            self.item_name,
            verify_type,
            count,
            item_set_name,
            multiply_value_specifying_quantity,
            user_id,
        )

    def verify_reference_of(
        self,
        reference_of: str,
        verify_type: str,
        item_set_name: Optional[str] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> VerifyReferenceOfByUserId:
        return VerifyReferenceOfByUserId(
            self.namespace_name,
            self.inventory_name,
            self.item_name,
            reference_of,
            verify_type,
            item_set_name,
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
                "model",
                self.inventory_name,
                "item",
                self.item_name,
            ],
        ).str(
        )
