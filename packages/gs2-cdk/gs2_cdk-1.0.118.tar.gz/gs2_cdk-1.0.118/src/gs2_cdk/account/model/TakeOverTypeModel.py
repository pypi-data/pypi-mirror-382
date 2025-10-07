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
from .ScopeValue import ScopeValue
from .OpenIdConnectSetting import OpenIdConnectSetting
from .options.TakeOverTypeModelOptions import TakeOverTypeModelOptions


class TakeOverTypeModel:
    type: int
    open_id_connect_setting: OpenIdConnectSetting
    metadata: Optional[str] = None

    def __init__(
        self,
        type: int,
        open_id_connect_setting: OpenIdConnectSetting,
        options: Optional[TakeOverTypeModelOptions] = TakeOverTypeModelOptions(),
    ):
        self.type = type
        self.open_id_connect_setting = open_id_connect_setting
        self.metadata = options.metadata if options.metadata else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.type is not None:
            properties["type"] = self.type
        if self.metadata is not None:
            properties["metadata"] = self.metadata
        if self.open_id_connect_setting is not None:
            properties["openIdConnectSetting"] = self.open_id_connect_setting.properties(
            )

        return properties
