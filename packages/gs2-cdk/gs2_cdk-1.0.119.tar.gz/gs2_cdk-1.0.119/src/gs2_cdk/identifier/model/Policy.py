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

from .Statement import Statement
from ...core.func import GetAttr, Join


class Policy:

    version: str = "2016-04-01"
    statements: List[Statement]

    def __init__(
            self,
            statements: List[Statement]
    ):
        self.statements = statements

    def properties(self) -> Dict[str, Any]:
        return {
            "Version": self.version,
            "Statements": [
                statement.properties()
                for statement in self.statements
            ],
        }
