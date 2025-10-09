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
from .AreaModel import AreaModel


class CurrentMasterData(CdkResource):
    version: str= "2022-08-28"
    namespace_name: str
    area_models: List[AreaModel]

    def __init__(
        self,
        stack: Stack,
        namespace_name: str,
        area_models: List[AreaModel],
    ):
        super().__init__(
            "MegaField_CurrentFieldMaster_" + namespace_name
        )

        self.namespace_name = namespace_name
        self.area_models = area_models
        stack.add_resource(
            self,
        )

    def alternate_keys(
        self,
    ):
        return self.namespace_name

    def resource_type(
        self,
    ) -> str:
        return "GS2::MegaField::CurrentFieldMaster"

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}
        settings: Dict[str, Any] = {}

        settings["version"] = self.version
        if self.area_models is not None:
            settings["areaModels"] = [
                v.properties(
                )
                for v in self.area_models
            ]

        if self.namespace_name is not None:
            properties["NamespaceName"] = self.namespace_name
        if settings is not None:
            properties["Settings"] = settings

        return properties