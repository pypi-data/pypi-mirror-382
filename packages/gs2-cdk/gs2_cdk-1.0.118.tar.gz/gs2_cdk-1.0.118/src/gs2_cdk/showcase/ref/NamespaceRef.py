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
from ..stamp_sheet.DecrementPurchaseCountByUserId import DecrementPurchaseCountByUserId
from ..stamp_sheet.ForceReDrawByUserId import ForceReDrawByUserId
from ..stamp_sheet.IncrementPurchaseCountByUserId import IncrementPurchaseCountByUserId


class NamespaceRef:
    namespace_name: str

    def __init__(
        self,
        namespace_name: str,
    ):
        self.namespace_name = namespace_name

    def decrement_purchase_count(
        self,
        showcase_name: str,
        display_item_name: str,
        count: int,
        user_id: Optional[str] = "#{userId}",
    ) -> DecrementPurchaseCountByUserId:
        return DecrementPurchaseCountByUserId(
            self.namespace_name,
            showcase_name,
            display_item_name,
            count,
            user_id,
        )

    def force_re_draw(
        self,
        showcase_name: str,
        user_id: Optional[str] = "#{userId}",
    ) -> ForceReDrawByUserId:
        return ForceReDrawByUserId(
            self.namespace_name,
            showcase_name,
            user_id,
        )

    def increment_purchase_count(
        self,
        showcase_name: str,
        display_item_name: str,
        count: int,
        user_id: Optional[str] = "#{userId}",
    ) -> IncrementPurchaseCountByUserId:
        return IncrementPurchaseCountByUserId(
            self.namespace_name,
            showcase_name,
            display_item_name,
            count,
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
                "showcase",
                self.namespace_name,
            ],
        ).str(
        )
