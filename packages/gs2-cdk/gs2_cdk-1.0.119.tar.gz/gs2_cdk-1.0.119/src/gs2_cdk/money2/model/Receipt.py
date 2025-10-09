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
from .options.ReceiptOptions import ReceiptOptions
from .enums.ReceiptStore import ReceiptStore


class Receipt:
    store: ReceiptStore
    transaction_i_d: str
    payload: str

    def __init__(
        self,
        store: ReceiptStore,
        transaction_i_d: str,
        payload: str,
        options: Optional[ReceiptOptions] = ReceiptOptions(),
    ):
        self.store = store
        self.transaction_i_d = transaction_i_d
        self.payload = payload

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.store is not None:
            properties["store"] = self.store.value
        if self.transaction_i_d is not None:
            properties["transactionID"] = self.transaction_i_d
        if self.payload is not None:
            properties["payload"] = self.payload

        return properties
