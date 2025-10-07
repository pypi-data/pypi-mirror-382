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
from .options.AcquireActionResultOptions import AcquireActionResultOptions


class AcquireActionResult:
    action: str
    acquire_request: str
    status_code: Optional[int] = None
    acquire_result: Optional[str] = None

    def __init__(
        self,
        action: str,
        acquire_request: str,
        options: Optional[AcquireActionResultOptions] = AcquireActionResultOptions(),
    ):
        self.action = action
        self.acquire_request = acquire_request
        self.status_code = options.status_code if options.status_code else None
        self.acquire_result = options.acquire_result if options.acquire_result else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.action is not None:
            properties["action"] = self.action.value
        if self.acquire_request is not None:
            properties["acquireRequest"] = self.acquire_request
        if self.status_code is not None:
            properties["statusCode"] = self.status_code
        if self.acquire_result is not None:
            properties["acquireResult"] = self.acquire_result

        return properties
