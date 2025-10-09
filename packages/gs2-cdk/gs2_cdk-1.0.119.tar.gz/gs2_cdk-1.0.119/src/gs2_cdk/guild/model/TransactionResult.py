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
from .VerifyActionResult import VerifyActionResult
from .ConsumeActionResult import ConsumeActionResult
from .AcquireActionResult import AcquireActionResult
from .options.TransactionResultOptions import TransactionResultOptions


class TransactionResult:
    transaction_id: str
    verify_results: Optional[List[VerifyActionResult]] = None
    consume_results: Optional[List[ConsumeActionResult]] = None
    acquire_results: Optional[List[AcquireActionResult]] = None

    def __init__(
        self,
        transaction_id: str,
        options: Optional[TransactionResultOptions] = TransactionResultOptions(),
    ):
        self.transaction_id = transaction_id
        self.verify_results = options.verify_results if options.verify_results else None
        self.consume_results = options.consume_results if options.consume_results else None
        self.acquire_results = options.acquire_results if options.acquire_results else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.transaction_id is not None:
            properties["transactionId"] = self.transaction_id
        if self.verify_results is not None:
            properties["verifyResults"] = [
                v.properties(
                )
                for v in self.verify_results
            ]
        if self.consume_results is not None:
            properties["consumeResults"] = [
                v.properties(
                )
                for v in self.consume_results
            ]
        if self.acquire_results is not None:
            properties["acquireResults"] = [
                v.properties(
                )
                for v in self.acquire_results
            ]

        return properties
