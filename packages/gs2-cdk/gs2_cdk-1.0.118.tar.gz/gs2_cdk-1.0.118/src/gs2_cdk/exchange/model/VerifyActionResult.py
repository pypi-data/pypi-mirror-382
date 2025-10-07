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
from .options.VerifyActionResultOptions import VerifyActionResultOptions


class VerifyActionResult:
    action: str
    verify_request: str
    status_code: Optional[int] = None
    verify_result: Optional[str] = None

    def __init__(
        self,
        action: str,
        verify_request: str,
        options: Optional[VerifyActionResultOptions] = VerifyActionResultOptions(),
    ):
        self.action = action
        self.verify_request = verify_request
        self.status_code = options.status_code if options.status_code else None
        self.verify_result = options.verify_result if options.verify_result else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.action is not None:
            properties["action"] = self.action.value
        if self.verify_request is not None:
            properties["verifyRequest"] = self.verify_request
        if self.status_code is not None:
            properties["statusCode"] = self.status_code
        if self.verify_result is not None:
            properties["verifyResult"] = self.verify_result

        return properties
