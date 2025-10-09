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
from .AppleAppStoreVerifyReceiptEvent import AppleAppStoreVerifyReceiptEvent
from .GooglePlayVerifyReceiptEvent import GooglePlayVerifyReceiptEvent
from .RefundEvent import RefundEvent
from .options.RefundHistoryOptions import RefundHistoryOptions


class RefundHistory:
    transaction_id: str
    year: int
    month: int
    day: int
    detail: RefundEvent
    user_id: Optional[str] = None

    def __init__(
        self,
        transaction_id: str,
        year: int,
        month: int,
        day: int,
        detail: RefundEvent,
        options: Optional[RefundHistoryOptions] = RefundHistoryOptions(),
    ):
        self.transaction_id = transaction_id
        self.year = year
        self.month = month
        self.day = day
        self.detail = detail
        self.user_id = options.user_id if options.user_id else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.transaction_id is not None:
            properties["transactionId"] = self.transaction_id
        if self.year is not None:
            properties["year"] = self.year
        if self.month is not None:
            properties["month"] = self.month
        if self.day is not None:
            properties["day"] = self.day
        if self.user_id is not None:
            properties["userId"] = self.user_id
        if self.detail is not None:
            properties["detail"] = self.detail.properties(
            )

        return properties
