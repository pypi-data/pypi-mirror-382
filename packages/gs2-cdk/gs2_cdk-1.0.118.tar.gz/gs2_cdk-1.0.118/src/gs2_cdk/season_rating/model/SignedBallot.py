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
from .options.SignedBallotOptions import SignedBallotOptions


class SignedBallot:
    body: str
    signature: str

    def __init__(
        self,
        body: str,
        signature: str,
        options: Optional[SignedBallotOptions] = SignedBallotOptions(),
    ):
        self.body = body
        self.signature = signature

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.body is not None:
            properties["body"] = self.body
        if self.signature is not None:
            properties["signature"] = self.signature

        return properties
