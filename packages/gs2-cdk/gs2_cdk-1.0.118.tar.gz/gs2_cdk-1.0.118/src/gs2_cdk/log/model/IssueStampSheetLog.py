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
from .options.IssueStampSheetLogOptions import IssueStampSheetLogOptions


class IssueStampSheetLog:
    timestamp: int
    transaction_id: str
    service: str
    method: str
    user_id: str
    action: str
    args: str
    tasks: Optional[List[str]] = None

    def __init__(
        self,
        timestamp: int,
        transaction_id: str,
        service: str,
        method: str,
        user_id: str,
        action: str,
        args: str,
        options: Optional[IssueStampSheetLogOptions] = IssueStampSheetLogOptions(),
    ):
        self.timestamp = timestamp
        self.transaction_id = transaction_id
        self.service = service
        self.method = method
        self.user_id = user_id
        self.action = action
        self.args = args
        self.tasks = options.tasks if options.tasks else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.timestamp is not None:
            properties["timestamp"] = self.timestamp
        if self.transaction_id is not None:
            properties["transactionId"] = self.transaction_id
        if self.service is not None:
            properties["service"] = self.service
        if self.method is not None:
            properties["method"] = self.method
        if self.user_id is not None:
            properties["userId"] = self.user_id
        if self.action is not None:
            properties["action"] = self.action
        if self.args is not None:
            properties["args"] = self.args
        if self.tasks is not None:
            properties["tasks"] = self.tasks

        return properties
