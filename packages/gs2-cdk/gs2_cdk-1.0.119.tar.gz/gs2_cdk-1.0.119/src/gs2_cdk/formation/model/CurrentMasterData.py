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
from .MoldModel import MoldModel
from .PropertyFormModel import PropertyFormModel


class CurrentMasterData(CdkResource):
    version: str= "2019-09-09"
    namespace_name: str
    mold_models: List[MoldModel]
    property_form_models: List[PropertyFormModel]

    def __init__(
        self,
        stack: Stack,
        namespace_name: str,
        mold_models: List[MoldModel],
        property_form_models: List[PropertyFormModel],
    ):
        super().__init__(
            "Formation_CurrentFormMaster_" + namespace_name
        )

        self.namespace_name = namespace_name
        self.mold_models = mold_models
        self.property_form_models = property_form_models
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
        return "GS2::Formation::CurrentFormMaster"

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}
        settings: Dict[str, Any] = {}

        settings["version"] = self.version
        if self.mold_models is not None:
            settings["moldModels"] = [
                v.properties(
                )
                for v in self.mold_models
            ]
        if self.property_form_models is not None:
            settings["propertyFormModels"] = [
                v.properties(
                )
                for v in self.property_form_models
            ]

        if self.namespace_name is not None:
            properties["NamespaceName"] = self.namespace_name
        if settings is not None:
            properties["Settings"] = settings

        return properties