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
from ...core.model import ConsumeAction
from ...core.model import AcquireAction
from .options.StampSheetResultOptions import StampSheetResultOptions


class StampSheetResult:
    user_id: str
    transaction_id: str
    sheet_request: AcquireAction
    task_requests: Optional[List[ConsumeAction]] = None
    task_result_codes: Optional[List[int]] = None
    task_results: Optional[List[str]] = None
    sheet_result_code: Optional[int] = None
    sheet_result: Optional[str] = None
    next_transaction_id: Optional[str] = None
    revision: Optional[int] = None

    def __init__(
        self,
        user_id: str,
        transaction_id: str,
        sheet_request: AcquireAction,
        options: Optional[StampSheetResultOptions] = StampSheetResultOptions(),
    ):
        self.user_id = user_id
        self.transaction_id = transaction_id
        self.sheet_request = sheet_request
        self.task_requests = options.task_requests if options.task_requests else None
        self.task_result_codes = options.task_result_codes if options.task_result_codes else None
        self.task_results = options.task_results if options.task_results else None
        self.sheet_result_code = options.sheet_result_code if options.sheet_result_code else None
        self.sheet_result = options.sheet_result if options.sheet_result else None
        self.next_transaction_id = options.next_transaction_id if options.next_transaction_id else None
        self.revision = options.revision if options.revision else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.user_id is not None:
            properties["userId"] = self.user_id
        if self.transaction_id is not None:
            properties["transactionId"] = self.transaction_id
        if self.task_requests is not None:
            properties["taskRequests"] = [
                v.properties(
                )
                for v in self.task_requests
            ]
        if self.sheet_request is not None:
            properties["sheetRequest"] = self.sheet_request.properties(
            )
        if self.task_result_codes is not None:
            properties["taskResultCodes"] = self.task_result_codes
        if self.task_results is not None:
            properties["taskResults"] = self.task_results
        if self.sheet_result_code is not None:
            properties["sheetResultCode"] = self.sheet_result_code
        if self.sheet_result is not None:
            properties["sheetResult"] = self.sheet_result
        if self.next_transaction_id is not None:
            properties["nextTransactionId"] = self.next_transaction_id

        return properties
