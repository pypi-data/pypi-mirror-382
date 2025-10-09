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
from .options.WithdrawEventOptions import WithdrawEventOptions


class WithdrawEvent:
    slot: int
    status: WalletSummary
    withdraw_details: Optional[List[DepositTransaction]] = None

    def __init__(
        self,
        slot: int,
        status: WalletSummary,
        options: Optional[WithdrawEventOptions] = WithdrawEventOptions(),
    ):
        self.slot = slot
        self.status = status
        self.withdraw_details = options.withdraw_details if options.withdraw_details else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.slot is not None:
            properties["slot"] = self.slot
        if self.withdraw_details is not None:
            properties["withdrawDetails"] = [
                v.properties(
                )
                for v in self.withdraw_details
            ]
        if self.status is not None:
            properties["status"] = self.status.properties(
            )

        return properties
