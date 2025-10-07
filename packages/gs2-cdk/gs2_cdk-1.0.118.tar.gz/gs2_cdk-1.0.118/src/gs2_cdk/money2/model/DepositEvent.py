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
from .DepositTransaction import DepositTransaction
from .WalletSummary import WalletSummary
from .options.DepositEventOptions import DepositEventOptions


class DepositEvent:
    slot: int
    status: WalletSummary
    deposit_transactions: Optional[List[DepositTransaction]] = None

    def __init__(
        self,
        slot: int,
        status: WalletSummary,
        options: Optional[DepositEventOptions] = DepositEventOptions(),
    ):
        self.slot = slot
        self.status = status
        self.deposit_transactions = options.deposit_transactions if options.deposit_transactions else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.slot is not None:
            properties["slot"] = self.slot
        if self.deposit_transactions is not None:
            properties["depositTransactions"] = [
                v.properties(
                )
                for v in self.deposit_transactions
            ]
        if self.status is not None:
            properties["status"] = self.status.properties(
            )

        return properties
