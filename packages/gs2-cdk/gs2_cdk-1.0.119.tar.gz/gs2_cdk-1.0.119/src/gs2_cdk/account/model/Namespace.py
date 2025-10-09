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
from .TakeOverTypeModel import TakeOverTypeModel

from .options.NamespaceOptions import NamespaceOptions


class Namespace(CdkResource):
    stack: Stack
    name: str
    description: Optional[str] = None
    transaction_setting: Optional[TransactionSetting] = None
    change_password_if_take_over: Optional[bool] = None
    different_user_id_for_login_and_data_retention: Optional[bool] = None
    create_account_script: Optional[ScriptSetting] = None
    authentication_script: Optional[ScriptSetting] = None
    create_take_over_script: Optional[ScriptSetting] = None
    do_take_over_script: Optional[ScriptSetting] = None
    ban_script: Optional[ScriptSetting] = None
    un_ban_script: Optional[ScriptSetting] = None
    log_setting: Optional[LogSetting] = None

    def __init__(
        self,
        stack: Stack,
        name: str,
        options: Optional[NamespaceOptions] = NamespaceOptions(),
    ):
        super().__init__(
            "Account_Namespace_" + name
        )

        self.stack = stack
        self.name = name
        self.description = options.description if options.description else None
        self.transaction_setting = options.transaction_setting if options.transaction_setting else None
        self.change_password_if_take_over = options.change_password_if_take_over if options.change_password_if_take_over else None
        self.different_user_id_for_login_and_data_retention = options.different_user_id_for_login_and_data_retention if options.different_user_id_for_login_and_data_retention else None
        self.create_account_script = options.create_account_script if options.create_account_script else None
        self.authentication_script = options.authentication_script if options.authentication_script else None
        self.create_take_over_script = options.create_take_over_script if options.create_take_over_script else None
        self.do_take_over_script = options.do_take_over_script if options.do_take_over_script else None
        self.ban_script = options.ban_script if options.ban_script else None
        self.un_ban_script = options.un_ban_script if options.un_ban_script else None
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
        return "GS2::Account::Namespace"

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
        if self.change_password_if_take_over is not None:
            properties["ChangePasswordIfTakeOver"] = self.change_password_if_take_over
        if self.different_user_id_for_login_and_data_retention is not None:
            properties["DifferentUserIdForLoginAndDataRetention"] = self.different_user_id_for_login_and_data_retention
        if self.create_account_script is not None:
            properties["CreateAccountScript"] = self.create_account_script.properties(
            )
        if self.authentication_script is not None:
            properties["AuthenticationScript"] = self.authentication_script.properties(
            )
        if self.create_take_over_script is not None:
            properties["CreateTakeOverScript"] = self.create_take_over_script.properties(
            )
        if self.do_take_over_script is not None:
            properties["DoTakeOverScript"] = self.do_take_over_script.properties(
            )
        if self.ban_script is not None:
            properties["BanScript"] = self.ban_script.properties(
            )
        if self.un_ban_script is not None:
            properties["UnBanScript"] = self.un_ban_script.properties(
            )
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
        take_over_type_models: List[TakeOverTypeModel],
    ) -> Namespace:
        CurrentMasterData(
            self.stack,
            self.name,
            take_over_type_models,
        ).add_depends_on(
            self,
        )
        return self
