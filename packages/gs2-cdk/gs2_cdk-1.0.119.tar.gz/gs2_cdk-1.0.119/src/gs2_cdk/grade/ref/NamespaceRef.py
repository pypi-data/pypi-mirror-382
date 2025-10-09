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
from .GradeModelRef import GradeModelRef
from ..stamp_sheet.AddGradeByUserId import AddGradeByUserId
from ..stamp_sheet.ApplyRankCapByUserId import ApplyRankCapByUserId
from ..stamp_sheet.MultiplyAcquireActionsByUserId import MultiplyAcquireActionsByUserId
from ...core.model import AcquireAction
from ..stamp_sheet.SubGradeByUserId import SubGradeByUserId
from ..stamp_sheet.VerifyGradeByUserId import VerifyGradeByUserId
from ..stamp_sheet.VerifyGradeUpMaterialByUserId import VerifyGradeUpMaterialByUserId


class NamespaceRef:
    namespace_name: str

    def __init__(
        self,
        namespace_name: str,
    ):
        self.namespace_name = namespace_name

    def grade_model(
        self,
        grade_name: str,
    ) -> GradeModelRef:
        return GradeModelRef(
            self.namespace_name,
            grade_name,
        )

    def add_grade(
        self,
        grade_name: str,
        property_id: str,
        grade_value: Optional[int] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> AddGradeByUserId:
        return AddGradeByUserId(
            self.namespace_name,
            grade_name,
            property_id,
            grade_value,
            user_id,
        )

    def apply_rank_cap(
        self,
        grade_name: str,
        property_id: str,
        user_id: Optional[str] = "#{userId}",
    ) -> ApplyRankCapByUserId:
        return ApplyRankCapByUserId(
            self.namespace_name,
            grade_name,
            property_id,
            user_id,
        )

    def multiply_acquire_actions(
        self,
        grade_name: str,
        property_id: str,
        rate_name: str,
        acquire_actions: Optional[List[AcquireAction]] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> MultiplyAcquireActionsByUserId:
        return MultiplyAcquireActionsByUserId(
            self.namespace_name,
            grade_name,
            property_id,
            rate_name,
            acquire_actions,
            user_id,
        )

    def sub_grade(
        self,
        grade_name: str,
        property_id: str,
        grade_value: Optional[int] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> SubGradeByUserId:
        return SubGradeByUserId(
            self.namespace_name,
            grade_name,
            property_id,
            grade_value,
            user_id,
        )

    def verify_grade(
        self,
        grade_name: str,
        verify_type: str,
        property_id: str,
        grade_value: Optional[int] = None,
        multiply_value_specifying_quantity: Optional[bool] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> VerifyGradeByUserId:
        return VerifyGradeByUserId(
            self.namespace_name,
            grade_name,
            verify_type,
            property_id,
            grade_value,
            multiply_value_specifying_quantity,
            user_id,
        )

    def verify_grade_up_material(
        self,
        grade_name: str,
        verify_type: str,
        property_id: str,
        material_property_id: str,
        user_id: Optional[str] = "#{userId}",
    ) -> VerifyGradeUpMaterialByUserId:
        return VerifyGradeUpMaterialByUserId(
            self.namespace_name,
            grade_name,
            verify_type,
            property_id,
            material_property_id,
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
                "grade",
                self.namespace_name,
            ],
        ).str(
        )
