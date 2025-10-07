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
from .QuestModelRef import QuestModelRef


class QuestGroupModelRef:
    namespace_name: str
    quest_group_name: str

    def __init__(
        self,
        namespace_name: str,
        quest_group_name: str,
    ):
        self.namespace_name = namespace_name
        self.quest_group_name = quest_group_name

    def quest_model(
        self,
        quest_name: str,
    ) -> QuestModelRef:
        return QuestModelRef(
            self.namespace_name,
            self.quest_group_name,
            quest_name,
        )

    def grn(
        self,
    ) -> str:
        return Join(
            ":",
            [
                "grn",
                "gs2",
                GetAttr.region(
                ).str(
                ),
                GetAttr.owner_id(
                ).str(
                ),
                "quest",
                self.namespace_name,
                "group",
                self.quest_group_name,
            ],
        ).str(
        )
