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
from .ExperienceModelRef import ExperienceModelRef
from ..stamp_sheet.AddExperienceByUserId import AddExperienceByUserId
from ..stamp_sheet.SetExperienceByUserId import SetExperienceByUserId
from ..stamp_sheet.AddRankCapByUserId import AddRankCapByUserId
from ..stamp_sheet.SetRankCapByUserId import SetRankCapByUserId
from ..stamp_sheet.MultiplyAcquireActionsByUserId import MultiplyAcquireActionsByUserId
from ...core.model import AcquireAction
from ..stamp_sheet.SubExperienceByUserId import SubExperienceByUserId
from ..stamp_sheet.SubRankCapByUserId import SubRankCapByUserId
from ..stamp_sheet.VerifyRankByUserId import VerifyRankByUserId
from ..stamp_sheet.VerifyRankCapByUserId import VerifyRankCapByUserId


class NamespaceRef:
    namespace_name: str

    def __init__(
        self,
        namespace_name: str,
    ):
        self.namespace_name = namespace_name

    def experience_model(
        self,
        experience_name: str,
    ) -> ExperienceModelRef:
        return ExperienceModelRef(
            self.namespace_name,
            experience_name,
        )

    def add_experience(
        self,
        experience_name: str,
        property_id: str,
        experience_value: Optional[int] = None,
        truncate_experience_when_rank_up: Optional[bool] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> AddExperienceByUserId:
        return AddExperienceByUserId(
            self.namespace_name,
            experience_name,
            property_id,
            experience_value,
            truncate_experience_when_rank_up,
            user_id,
        )

    def set_experience(
        self,
        experience_name: str,
        property_id: str,
        experience_value: Optional[int] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> SetExperienceByUserId:
        return SetExperienceByUserId(
            self.namespace_name,
            experience_name,
            property_id,
            experience_value,
            user_id,
        )

    def add_rank_cap(
        self,
        experience_name: str,
        property_id: str,
        rank_cap_value: int,
        user_id: Optional[str] = "#{userId}",
    ) -> AddRankCapByUserId:
        return AddRankCapByUserId(
            self.namespace_name,
            experience_name,
            property_id,
            rank_cap_value,
            user_id,
        )

    def set_rank_cap(
        self,
        experience_name: str,
        property_id: str,
        rank_cap_value: int,
        user_id: Optional[str] = "#{userId}",
    ) -> SetRankCapByUserId:
        return SetRankCapByUserId(
            self.namespace_name,
            experience_name,
            property_id,
            rank_cap_value,
            user_id,
        )

    def multiply_acquire_actions(
        self,
        experience_name: str,
        property_id: str,
        rate_name: str,
        acquire_actions: Optional[List[AcquireAction]] = None,
        base_rate: Optional[float] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> MultiplyAcquireActionsByUserId:
        return MultiplyAcquireActionsByUserId(
            self.namespace_name,
            experience_name,
            property_id,
            rate_name,
            acquire_actions,
            base_rate,
            user_id,
        )

    def sub_experience(
        self,
        experience_name: str,
        property_id: str,
        experience_value: Optional[int] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> SubExperienceByUserId:
        return SubExperienceByUserId(
            self.namespace_name,
            experience_name,
            property_id,
            experience_value,
            user_id,
        )

    def sub_rank_cap(
        self,
        experience_name: str,
        property_id: str,
        rank_cap_value: int,
        user_id: Optional[str] = "#{userId}",
    ) -> SubRankCapByUserId:
        return SubRankCapByUserId(
            self.namespace_name,
            experience_name,
            property_id,
            rank_cap_value,
            user_id,
        )

    def verify_rank(
        self,
        experience_name: str,
        verify_type: str,
        property_id: str,
        rank_value: Optional[int] = None,
        multiply_value_specifying_quantity: Optional[bool] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> VerifyRankByUserId:
        return VerifyRankByUserId(
            self.namespace_name,
            experience_name,
            verify_type,
            property_id,
            rank_value,
            multiply_value_specifying_quantity,
            user_id,
        )

    def verify_rank_cap(
        self,
        experience_name: str,
        verify_type: str,
        property_id: str,
        rank_cap_value: int,
        multiply_value_specifying_quantity: Optional[bool] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> VerifyRankCapByUserId:
        return VerifyRankCapByUserId(
            self.namespace_name,
            experience_name,
            verify_type,
            property_id,
            rank_cap_value,
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
                "experience",
                self.namespace_name,
            ],
        ).str(
        )
