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
from .options.DailyTransactionHistoryOptions import DailyTransactionHistoryOptions


class DailyTransactionHistory:
    year: int
    month: int
    day: int
    currency: str
    deposit_amount: float
    withdraw_amount: float
    issue_count: int
    consume_count: int
    revision: Optional[int] = None

    def __init__(
        self,
        year: int,
        month: int,
        day: int,
        currency: str,
        deposit_amount: float,
        withdraw_amount: float,
        issue_count: int,
        consume_count: int,
        options: Optional[DailyTransactionHistoryOptions] = DailyTransactionHistoryOptions(),
    ):
        self.year = year
        self.month = month
        self.day = day
        self.currency = currency
        self.deposit_amount = deposit_amount
        self.withdraw_amount = withdraw_amount
        self.issue_count = issue_count
        self.consume_count = consume_count
        self.revision = options.revision if options.revision else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.year is not None:
            properties["year"] = self.year
        if self.month is not None:
            properties["month"] = self.month
        if self.day is not None:
            properties["day"] = self.day
        if self.currency is not None:
            properties["currency"] = self.currency
        if self.deposit_amount is not None:
            properties["depositAmount"] = self.deposit_amount
        if self.withdraw_amount is not None:
            properties["withdrawAmount"] = self.withdraw_amount
        if self.issue_count is not None:
            properties["issueCount"] = self.issue_count
        if self.consume_count is not None:
            properties["consumeCount"] = self.consume_count

        return properties
