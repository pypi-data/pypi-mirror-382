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
from ..stamp_sheet.DepositByUserId import DepositByUserId
from ..stamp_sheet.RevertRecordReceipt import RevertRecordReceipt
from ..stamp_sheet.WithdrawByUserId import WithdrawByUserId
from ..stamp_sheet.RecordReceipt import RecordReceipt


class NamespaceRef:
    namespace_name: str

    def __init__(
        self,
        namespace_name: str,
    ):
        self.namespace_name = namespace_name

    def deposit(
        self,
        slot: int,
        price: float,
        count: int,
        user_id: Optional[str] = "#{userId}",
    ) -> DepositByUserId:
        return DepositByUserId(
            self.namespace_name,
            slot,
            price,
            count,
            user_id,
        )

    def revert_record_receipt(
        self,
        receipt: str,
        user_id: Optional[str] = "#{userId}",
    ) -> RevertRecordReceipt:
        return RevertRecordReceipt(
            self.namespace_name,
            receipt,
            user_id,
        )

    def withdraw(
        self,
        slot: int,
        count: int,
        paid_only: Optional[bool] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> WithdrawByUserId:
        return WithdrawByUserId(
            self.namespace_name,
            slot,
            count,
            paid_only,
            user_id,
        )

    def record_receipt(
        self,
        contents_id: str,
        receipt: str,
        user_id: Optional[str] = "#{userId}",
    ) -> RecordReceipt:
        return RecordReceipt(
            self.namespace_name,
            contents_id,
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
                "money",
                self.namespace_name,
            ],
        ).str(
        )
