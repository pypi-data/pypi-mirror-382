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
from .UnleashRateModelRef import UnleashRateModelRef
from .RateModelRef import RateModelRef
from ..stamp_sheet.CreateProgressByUserId import CreateProgressByUserId
from ..model.Material import Material
from ..stamp_sheet.DeleteProgressByUserId import DeleteProgressByUserId


class NamespaceRef:
    namespace_name: str

    def __init__(
        self,
        namespace_name: str,
    ):
        self.namespace_name = namespace_name

    def unleash_rate_model(
        self,
        rate_name: str,
    ) -> UnleashRateModelRef:
        return UnleashRateModelRef(
            self.namespace_name,
            rate_name,
        )

    def rate_model(
        self,
        rate_name: str,
    ) -> RateModelRef:
        return RateModelRef(
            self.namespace_name,
            rate_name,
        )

    def create_progress(
        self,
        rate_name: str,
        target_item_set_id: str,
        materials: Optional[List[Material]] = None,
        force: Optional[bool] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> CreateProgressByUserId:
        return CreateProgressByUserId(
            self.namespace_name,
            rate_name,
            target_item_set_id,
            materials,
            force,
            user_id,
        )

    def delete_progress(
        self,
        user_id: Optional[str] = "#{userId}",
    ) -> DeleteProgressByUserId:
        return DeleteProgressByUserId(
            self.namespace_name,
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
                "enhance",
                self.namespace_name,
            ],
        ).str(
        )
