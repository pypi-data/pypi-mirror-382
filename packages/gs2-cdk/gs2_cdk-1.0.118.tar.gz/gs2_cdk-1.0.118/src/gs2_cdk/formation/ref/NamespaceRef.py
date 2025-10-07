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
from .MoldModelRef import MoldModelRef
from .PropertyFormModelRef import PropertyFormModelRef
from ..stamp_sheet.AddMoldCapacityByUserId import AddMoldCapacityByUserId
from ..stamp_sheet.SetMoldCapacityByUserId import SetMoldCapacityByUserId
from ..stamp_sheet.AcquireActionsToFormProperties import AcquireActionsToFormProperties
from ...core.model import AcquireAction
from ...core.model import Config
from ..stamp_sheet.SetFormByUserId import SetFormByUserId
from ..stamp_sheet.AcquireActionsToPropertyFormProperties import AcquireActionsToPropertyFormProperties
from ..stamp_sheet.SubMoldCapacityByUserId import SubMoldCapacityByUserId


class NamespaceRef:
    namespace_name: str

    def __init__(
        self,
        namespace_name: str,
    ):
        self.namespace_name = namespace_name

    def mold_model(
        self,
        mold_model_name: str,
    ) -> MoldModelRef:
        return MoldModelRef(
            self.namespace_name,
            mold_model_name,
        )

    def property_form_model(
        self,
        property_form_model_name: str,
    ) -> PropertyFormModelRef:
        return PropertyFormModelRef(
            self.namespace_name,
            property_form_model_name,
        )

    def add_mold_capacity(
        self,
        mold_model_name: str,
        capacity: int,
        user_id: Optional[str] = "#{userId}",
    ) -> AddMoldCapacityByUserId:
        return AddMoldCapacityByUserId(
            self.namespace_name,
            mold_model_name,
            capacity,
            user_id,
        )

    def set_mold_capacity(
        self,
        mold_model_name: str,
        capacity: int,
        user_id: Optional[str] = "#{userId}",
    ) -> SetMoldCapacityByUserId:
        return SetMoldCapacityByUserId(
            self.namespace_name,
            mold_model_name,
            capacity,
            user_id,
        )

    def acquire_actions_to_form_properties(
        self,
        mold_model_name: str,
        index: int,
        acquire_action: AcquireAction,
        config: Optional[List[Config]] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> AcquireActionsToFormProperties:
        return AcquireActionsToFormProperties(
            self.namespace_name,
            mold_model_name,
            index,
            acquire_action,
            config,
            user_id,
        )

    def set_form(
        self,
        mold_model_name: str,
        index: int,
        slots: List[Slot],
        user_id: Optional[str] = "#{userId}",
    ) -> SetFormByUserId:
        return SetFormByUserId(
            self.namespace_name,
            mold_model_name,
            index,
            slots,
            user_id,
        )

    def acquire_actions_to_property_form_properties(
        self,
        property_form_model_name: str,
        property_id: str,
        acquire_action: AcquireAction,
        config: Optional[List[Config]] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> AcquireActionsToPropertyFormProperties:
        return AcquireActionsToPropertyFormProperties(
            self.namespace_name,
            property_form_model_name,
            property_id,
            acquire_action,
            config,
            user_id,
        )

    def sub_mold_capacity(
        self,
        mold_model_name: str,
        capacity: int,
        user_id: Optional[str] = "#{userId}",
    ) -> SubMoldCapacityByUserId:
        return SubMoldCapacityByUserId(
            self.namespace_name,
            mold_model_name,
            capacity,
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
                "formation",
                self.namespace_name,
            ],
        ).str(
        )
