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

from ...core.func import GetAttr, Join


class Statement:

    effect: str
    actions: List[str]

    @staticmethod
    def allow(
            actions: List[str],
    ) -> Statement:
        statement = Statement()
        statement.effect = "Allow"
        statement.actions = actions
        return statement

    @staticmethod
    def allow_all() -> Statement:
        statement = Statement()
        statement.effect = "Allow"
        statement.actions = ['*']
        return statement

    @staticmethod
    def deny(
            actions: List[str],
    ) -> Statement:
        statement = Statement()
        statement.effect = "Deny"
        statement.actions = actions
        return statement

    @staticmethod
    def deny_all() -> Statement:
        statement = Statement()
        statement.effect = "Deny"
        statement.actions = ['*']
        return statement

    def action(self, action: str) -> Statement:
        self.actions.append(action)
        return self

    def properties(self) -> Dict[str, Any]:
        return {
            "Effect": self.effect,
            "Actions": [
                action
                for action in self.actions
            ],
            "Resources": ['*']
        }
