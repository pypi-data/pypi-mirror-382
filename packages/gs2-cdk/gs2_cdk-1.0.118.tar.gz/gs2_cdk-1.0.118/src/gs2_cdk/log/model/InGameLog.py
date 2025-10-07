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
from .InGameLogTag import InGameLogTag
from .options.InGameLogOptions import InGameLogOptions


class InGameLog:
    timestamp: int
    request_id: str
    payload: str
    user_id: Optional[str] = None
    tags: Optional[List[InGameLogTag]] = None

    def __init__(
        self,
        timestamp: int,
        request_id: str,
        payload: str,
        options: Optional[InGameLogOptions] = InGameLogOptions(),
    ):
        self.timestamp = timestamp
        self.request_id = request_id
        self.payload = payload
        self.user_id = options.user_id if options.user_id else None
        self.tags = options.tags if options.tags else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.timestamp is not None:
            properties["timestamp"] = self.timestamp
        if self.request_id is not None:
            properties["requestId"] = self.request_id
        if self.user_id is not None:
            properties["userId"] = self.user_id
        if self.tags is not None:
            properties["tags"] = [
                v.properties(
                )
                for v in self.tags
            ]
        if self.payload is not None:
            properties["payload"] = self.payload

        return properties
