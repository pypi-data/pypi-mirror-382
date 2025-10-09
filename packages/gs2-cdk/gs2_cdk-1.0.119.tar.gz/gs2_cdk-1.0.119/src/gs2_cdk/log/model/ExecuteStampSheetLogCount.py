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
from .options.ExecuteStampSheetLogCountOptions import ExecuteStampSheetLogCountOptions


class ExecuteStampSheetLogCount:
    count: int
    service: Optional[str] = None
    method: Optional[str] = None
    user_id: Optional[str] = None
    action: Optional[str] = None

    def __init__(
        self,
        count: int,
        options: Optional[ExecuteStampSheetLogCountOptions] = ExecuteStampSheetLogCountOptions(),
    ):
        self.count = count
        self.service = options.service if options.service else None
        self.method = options.method if options.method else None
        self.user_id = options.user_id if options.user_id else None
        self.action = options.action if options.action else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.service is not None:
            properties["service"] = self.service
        if self.method is not None:
            properties["method"] = self.method
        if self.user_id is not None:
            properties["userId"] = self.user_id
        if self.action is not None:
            properties["action"] = self.action
        if self.count is not None:
            properties["count"] = self.count

        return properties
