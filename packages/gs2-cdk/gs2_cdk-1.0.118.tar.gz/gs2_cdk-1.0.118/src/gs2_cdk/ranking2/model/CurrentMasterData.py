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
from .GlobalRankingModel import GlobalRankingModel
from .ClusterRankingModel import ClusterRankingModel
from .SubscribeRankingModel import SubscribeRankingModel


class CurrentMasterData(CdkResource):
    version: str= "2024-05-30"
    namespace_name: str
    global_ranking_models: List[GlobalRankingModel]
    cluster_ranking_models: List[ClusterRankingModel]
    subscribe_ranking_models: List[SubscribeRankingModel]

    def __init__(
        self,
        stack: Stack,
        namespace_name: str,
        global_ranking_models: List[GlobalRankingModel],
        cluster_ranking_models: List[ClusterRankingModel],
        subscribe_ranking_models: List[SubscribeRankingModel],
    ):
        super().__init__(
            "Ranking2_CurrentRankingMaster_" + namespace_name
        )

        self.namespace_name = namespace_name
        self.global_ranking_models = global_ranking_models
        self.cluster_ranking_models = cluster_ranking_models
        self.subscribe_ranking_models = subscribe_ranking_models
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
        return "GS2::Ranking2::CurrentRankingMaster"

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}
        settings: Dict[str, Any] = {}

        settings["version"] = self.version
        if self.global_ranking_models is not None:
            settings["globalRankingModels"] = [
                v.properties(
                )
                for v in self.global_ranking_models
            ]
        if self.cluster_ranking_models is not None:
            settings["clusterRankingModels"] = [
                v.properties(
                )
                for v in self.cluster_ranking_models
            ]
        if self.subscribe_ranking_models is not None:
            settings["subscribeRankingModels"] = [
                v.properties(
                )
                for v in self.subscribe_ranking_models
            ]

        if self.namespace_name is not None:
            properties["NamespaceName"] = self.namespace_name
        if settings is not None:
            properties["Settings"] = settings

        return properties