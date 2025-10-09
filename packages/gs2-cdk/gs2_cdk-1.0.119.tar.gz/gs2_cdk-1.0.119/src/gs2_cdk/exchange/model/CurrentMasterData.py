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
from .RateModel import RateModel
from .IncrementalRateModel import IncrementalRateModel


class CurrentMasterData(CdkResource):
    version: str= "2019-08-19"
    namespace_name: str
    rate_models: List[RateModel]
    incremental_rate_models: List[IncrementalRateModel]

    def __init__(
        self,
        stack: Stack,
        namespace_name: str,
        rate_models: List[RateModel],
        incremental_rate_models: List[IncrementalRateModel],
    ):
        super().__init__(
            "Exchange_CurrentRateMaster_" + namespace_name
        )

        self.namespace_name = namespace_name
        self.rate_models = rate_models
        self.incremental_rate_models = incremental_rate_models
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
        return "GS2::Exchange::CurrentRateMaster"

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}
        settings: Dict[str, Any] = {}

        settings["version"] = self.version
        if self.rate_models is not None:
            settings["rateModels"] = [
                v.properties(
                )
                for v in self.rate_models
            ]
        if self.incremental_rate_models is not None:
            settings["incrementalRateModels"] = [
                v.properties(
                )
                for v in self.incremental_rate_models
            ]

        if self.namespace_name is not None:
            properties["NamespaceName"] = self.namespace_name
        if settings is not None:
            properties["Settings"] = settings

        return properties