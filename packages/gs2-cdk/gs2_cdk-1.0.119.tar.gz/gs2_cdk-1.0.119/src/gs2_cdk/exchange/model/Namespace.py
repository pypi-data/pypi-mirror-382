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
from .RateModel import RateModel
from .IncrementalRateModel import IncrementalRateModel

from .options.NamespaceOptions import NamespaceOptions


class Namespace(CdkResource):
    stack: Stack
    name: str
    description: Optional[str] = None
    enable_await_exchange: Optional[bool] = None
    enable_direct_exchange: Optional[bool] = None
    transaction_setting: Optional[TransactionSetting] = None
    exchange_script: Optional[ScriptSetting] = None
    incremental_exchange_script: Optional[ScriptSetting] = None
    acquire_await_script: Optional[ScriptSetting] = None
    log_setting: Optional[LogSetting] = None

    def __init__(
        self,
        stack: Stack,
        name: str,
        options: Optional[NamespaceOptions] = NamespaceOptions(),
    ):
        super().__init__(
            "Exchange_Namespace_" + name
        )

        self.stack = stack
        self.name = name
        self.description = options.description if options.description else None
        self.enable_await_exchange = options.enable_await_exchange if options.enable_await_exchange else None
        self.enable_direct_exchange = options.enable_direct_exchange if options.enable_direct_exchange else None
        self.transaction_setting = options.transaction_setting if options.transaction_setting else None
        self.exchange_script = options.exchange_script if options.exchange_script else None
        self.incremental_exchange_script = options.incremental_exchange_script if options.incremental_exchange_script else None
        self.acquire_await_script = options.acquire_await_script if options.acquire_await_script else None
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
        return "GS2::Exchange::Namespace"

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.name is not None:
            properties["Name"] = self.name
        if self.description is not None:
            properties["Description"] = self.description
        if self.enable_await_exchange is not None:
            properties["EnableAwaitExchange"] = self.enable_await_exchange
        if self.enable_direct_exchange is not None:
            properties["EnableDirectExchange"] = self.enable_direct_exchange
        if self.transaction_setting is not None:
            properties["TransactionSetting"] = self.transaction_setting.properties(
            )
        if self.exchange_script is not None:
            properties["ExchangeScript"] = self.exchange_script.properties(
            )
        if self.incremental_exchange_script is not None:
            properties["IncrementalExchangeScript"] = self.incremental_exchange_script.properties(
            )
        if self.acquire_await_script is not None:
            properties["AcquireAwaitScript"] = self.acquire_await_script.properties(
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
        rate_models: List[RateModel],
        incremental_rate_models: List[IncrementalRateModel],
    ) -> Namespace:
        CurrentMasterData(
            self.stack,
            self.name,
            rate_models,
            incremental_rate_models,
        ).add_depends_on(
            self,
        )
        return self
