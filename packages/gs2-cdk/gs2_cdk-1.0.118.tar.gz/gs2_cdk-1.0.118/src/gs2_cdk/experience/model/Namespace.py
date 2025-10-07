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

from ...core.model import CdkResource, Stack
from ...core.func import GetAttr
from ...core.model import TransactionSetting
from ...core.model import ScriptSetting
from ...core.model import LogSetting

from ..ref.NamespaceRef import NamespaceRef
from .CurrentMasterData import CurrentMasterData
from .ExperienceModel import ExperienceModel

from .options.NamespaceOptions import NamespaceOptions


class Namespace(CdkResource):
    stack: Stack
    name: str
    description: Optional[str] = None
    transaction_setting: Optional[TransactionSetting] = None
    rank_cap_script_id: Optional[str] = None
    change_experience_script: Optional[ScriptSetting] = None
    change_rank_script: Optional[ScriptSetting] = None
    change_rank_cap_script: Optional[ScriptSetting] = None
    overflow_experience_script: Optional[str] = None
    log_setting: Optional[LogSetting] = None

    def __init__(
        self,
        stack: Stack,
        name: str,
        options: Optional[NamespaceOptions] = NamespaceOptions(),
    ):
        super().__init__(
            "Experience_Namespace_" + name
        )

        self.stack = stack
        self.name = name
        self.description = options.description if options.description else None
        self.transaction_setting = options.transaction_setting if options.transaction_setting else None
        self.rank_cap_script_id = options.rank_cap_script_id if options.rank_cap_script_id else None
        self.change_experience_script = options.change_experience_script if options.change_experience_script else None
        self.change_rank_script = options.change_rank_script if options.change_rank_script else None
        self.change_rank_cap_script = options.change_rank_cap_script if options.change_rank_cap_script else None
        self.overflow_experience_script = options.overflow_experience_script if options.overflow_experience_script else None
        self.log_setting = options.log_setting if options.log_setting else None
        stack.add_resource(
            self,
        )


    def alternate_keys(
        self,
    ):
        return "name"

    def resource_type(
        self,
    ) -> str:
        return "GS2::Experience::Namespace"

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.name is not None:
            properties["Name"] = self.name
        if self.description is not None:
            properties["Description"] = self.description
        if self.transaction_setting is not None:
            properties["TransactionSetting"] = self.transaction_setting.properties(
            )
        if self.rank_cap_script_id is not None:
            properties["RankCapScriptId"] = self.rank_cap_script_id
        if self.change_experience_script is not None:
            properties["ChangeExperienceScript"] = self.change_experience_script.properties(
            )
        if self.change_rank_script is not None:
            properties["ChangeRankScript"] = self.change_rank_script.properties(
            )
        if self.change_rank_cap_script is not None:
            properties["ChangeRankCapScript"] = self.change_rank_cap_script.properties(
            )
        if self.overflow_experience_script is not None:
            properties["OverflowExperienceScript"] = self.overflow_experience_script
        if self.log_setting is not None:
            properties["LogSetting"] = self.log_setting.properties(
            )

        return properties

    def ref(
        self,
    ) -> NamespaceRef:
        return NamespaceRef(
            self.name,
        )

    def get_attr_namespace_id(
        self,
    ) -> GetAttr:
        return GetAttr(
            self,
            "Item.NamespaceId",
            None,
        )

    def master_data(
        self,
        experience_models: List[ExperienceModel],
    ) -> Namespace:
        CurrentMasterData(
            self.stack,
            self.name,
            experience_models,
        ).add_depends_on(
            self,
        )
        return self
