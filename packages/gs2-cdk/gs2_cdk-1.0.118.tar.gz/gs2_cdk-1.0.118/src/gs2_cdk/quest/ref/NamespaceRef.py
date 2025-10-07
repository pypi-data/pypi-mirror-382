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
from .QuestGroupModelRef import QuestGroupModelRef
from ..stamp_sheet.CreateProgressByUserId import CreateProgressByUserId
from ...core.model import Config
from ..stamp_sheet.DeleteProgressByUserId import DeleteProgressByUserId


class NamespaceRef:
    namespace_name: str

    def __init__(
        self,
        namespace_name: str,
    ):
        self.namespace_name = namespace_name

    def quest_group_model(
        self,
        quest_group_name: str,
    ) -> QuestGroupModelRef:
        return QuestGroupModelRef(
            self.namespace_name,
            quest_group_name,
        )

    def create_progress(
        self,
        quest_model_id: str,
        force: Optional[bool] = None,
        config: Optional[List[Config]] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> CreateProgressByUserId:
        return CreateProgressByUserId(
            self.namespace_name,
            quest_model_id,
            force,
            config,
            user_id,
        )

    def delete_progress(
        self,
        user_id: Optional[str] = "#{userId}",
    ) -> DeleteProgressByUserId:
        return DeleteProgressByUserId(
            self.namespace_name,
            user_id,
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
            ],
        ).str(
        )
