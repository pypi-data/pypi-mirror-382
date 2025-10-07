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
from .enums.NamespacePriority import NamespacePriority
from .enums.NamespaceCurrency import NamespaceCurrency

from .options.NamespaceOptions import NamespaceOptions


class Namespace(CdkResource):
    stack: Stack
    name: str
    priority: NamespacePriority
    share_free: bool
    currency: NamespaceCurrency
    description: Optional[str] = None
    transaction_setting: Optional[TransactionSetting] = None
    apple_key: Optional[str] = None
    google_key: Optional[str] = None
    enable_fake_receipt: Optional[bool] = None
    create_wallet_script: Optional[ScriptSetting] = None
    deposit_script: Optional[ScriptSetting] = None
    withdraw_script: Optional[ScriptSetting] = None
    log_setting: Optional[LogSetting] = None

    def __init__(
        self,
        stack: Stack,
        name: str,
        priority: NamespacePriority,
        share_free: bool,
        currency: NamespaceCurrency,
        options: Optional[NamespaceOptions] = NamespaceOptions(),
    ):
        super().__init__(
            "Money_Namespace_" + name
        )

        self.stack = stack
        self.name = name
        self.priority = priority
        self.share_free = share_free
        self.currency = currency
        self.description = options.description if options.description else None
        self.transaction_setting = options.transaction_setting if options.transaction_setting else None
        self.apple_key = options.apple_key if options.apple_key else None
        self.google_key = options.google_key if options.google_key else None
        self.enable_fake_receipt = options.enable_fake_receipt if options.enable_fake_receipt else None
        self.create_wallet_script = options.create_wallet_script if options.create_wallet_script else None
        self.deposit_script = options.deposit_script if options.deposit_script else None
        self.withdraw_script = options.withdraw_script if options.withdraw_script else None
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
        return "GS2::Money::Namespace"

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
        if self.priority is not None:
            properties["Priority"] = self.priority
        if self.share_free is not None:
            properties["ShareFree"] = self.share_free
        if self.currency is not None:
            properties["Currency"] = self.currency
        if self.apple_key is not None:
            properties["AppleKey"] = self.apple_key
        if self.google_key is not None:
            properties["GoogleKey"] = self.google_key
        if self.enable_fake_receipt is not None:
            properties["EnableFakeReceipt"] = self.enable_fake_receipt
        if self.create_wallet_script is not None:
            properties["CreateWalletScript"] = self.create_wallet_script.properties(
            )
        if self.deposit_script is not None:
            properties["DepositScript"] = self.deposit_script.properties(
            )
        if self.withdraw_script is not None:
            properties["WithdrawScript"] = self.withdraw_script.properties(
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
