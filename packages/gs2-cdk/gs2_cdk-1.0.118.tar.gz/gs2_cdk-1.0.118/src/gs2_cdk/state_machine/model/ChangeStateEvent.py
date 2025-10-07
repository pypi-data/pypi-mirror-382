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
from .options.ChangeStateEventOptions import ChangeStateEventOptions


class ChangeStateEvent:
    task_name: str
    hash: str
    timestamp: int

    def __init__(
        self,
        task_name: str,
        hash: str,
        timestamp: int,
        options: Optional[ChangeStateEventOptions] = ChangeStateEventOptions(),
    ):
        self.task_name = task_name
        self.hash = hash
        self.timestamp = timestamp

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.task_name is not None:
            properties["taskName"] = self.task_name
        if self.hash is not None:
            properties["hash"] = self.hash
        if self.timestamp is not None:
            properties["timestamp"] = self.timestamp

        return properties
