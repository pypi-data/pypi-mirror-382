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
from ...core.model import VerifyAction
from ...core.model import ConsumeAction
from ...core.model import AcquireAction
from .options.SalesItemOptions import SalesItemOptions


class SalesItem:
    name: str
    acquire_actions: List[AcquireAction]
    metadata: Optional[str] = None
    verify_actions: Optional[List[VerifyAction]] = None
    consume_actions: Optional[List[ConsumeAction]] = None

    def __init__(
        self,
        name: str,
        acquire_actions: List[AcquireAction],
        options: Optional[SalesItemOptions] = SalesItemOptions(),
    ):
        self.name = name
        self.acquire_actions = acquire_actions
        self.metadata = options.metadata if options.metadata else None
        self.verify_actions = options.verify_actions if options.verify_actions else None
        self.consume_actions = options.consume_actions if options.consume_actions else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.name is not None:
            properties["name"] = self.name
        if self.metadata is not None:
            properties["metadata"] = self.metadata
        if self.verify_actions is not None:
            properties["verifyActions"] = [
                v.properties(
                )
                for v in self.verify_actions
            ]
        if self.consume_actions is not None:
            properties["consumeActions"] = [
                v.properties(
                )
                for v in self.consume_actions
            ]
        if self.acquire_actions is not None:
            properties["acquireActions"] = [
                v.properties(
                )
                for v in self.acquire_actions
            ]

        return properties
