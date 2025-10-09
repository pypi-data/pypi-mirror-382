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
#
# deny overwrite
from __future__ import annotations
from typing import *

from ...core.func import GetAttr, Join
from .DailyTransactionHistoryRef import DailyTransactionHistoryRef
from .StoreContentModelRef import StoreContentModelRef
from .UnusedBalanceRef import UnusedBalanceRef
from ..stamp_sheet.DepositByUserId import DepositByUserId
from ..model.DepositTransaction import DepositTransaction
from ..stamp_sheet.WithdrawByUserId import WithdrawByUserId
from ..stamp_sheet.VerifyReceiptByUserId import VerifyReceiptByUserId
from ..model.Receipt import Receipt


class NamespaceRef:
    namespace_name: str

    def __init__(
        self,
        namespace_name: str,
    ):
        self.namespace_name = namespace_name

    def store_content_model(
        self,
        content_name: str,
    ) -> StoreContentModelRef:
        return StoreContentModelRef(
            self.namespace_name,
            content_name,
        )

    def deposit(
        self,
        slot: int,
        deposit_transactions: List[DepositTransaction],
        user_id: Optional[str] = "#{userId}",
    ) -> DepositByUserId:
        return DepositByUserId(
            self.namespace_name,
            slot,
            deposit_transactions,
            user_id,
        )

    def withdraw(
        self,
        slot: int,
        withdraw_count: int,
        paid_only: Optional[bool] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> WithdrawByUserId:
        return WithdrawByUserId(
            self.namespace_name,
            slot,
            withdraw_count,
            paid_only,
            user_id,
        )

    def verify_receipt(
        self,
        content_name: str,
        receipt: Optional[str] = "#{receipt}",
        user_id: Optional[str] = "#{userId}",
    ) -> VerifyReceiptByUserId:
        return VerifyReceiptByUserId(
            self.namespace_name,
            content_name,
            receipt,
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
                "money2",
                self.namespace_name,
            ],
        ).str(
        )
