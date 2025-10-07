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
from .options.ConsumeActionResultOptions import ConsumeActionResultOptions


class ConsumeActionResult:
    action: str
    consume_request: str
    status_code: Optional[int] = None
    consume_result: Optional[str] = None

    def __init__(
        self,
        action: str,
        consume_request: str,
        options: Optional[ConsumeActionResultOptions] = ConsumeActionResultOptions(),
    ):
        self.action = action
        self.consume_request = consume_request
        self.status_code = options.status_code if options.status_code else None
        self.consume_result = options.consume_result if options.consume_result else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.action is not None:
            properties["action"] = self.action.value
        if self.consume_request is not None:
            properties["consumeRequest"] = self.consume_request
        if self.status_code is not None:
            properties["statusCode"] = self.status_code
        if self.consume_result is not None:
            properties["consumeResult"] = self.consume_result

        return properties
