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
from .GlobalRankingModelRef import GlobalRankingModelRef
from .SubscribeRankingModelRef import SubscribeRankingModelRef
from .ClusterRankingModelRef import ClusterRankingModelRef
from ..stamp_sheet.CreateGlobalRankingReceivedRewardByUserId import CreateGlobalRankingReceivedRewardByUserId
from ..stamp_sheet.CreateClusterRankingReceivedRewardByUserId import CreateClusterRankingReceivedRewardByUserId
from ..stamp_sheet.VerifyGlobalRankingScoreByUserId import VerifyGlobalRankingScoreByUserId
from ..stamp_sheet.VerifyClusterRankingScoreByUserId import VerifyClusterRankingScoreByUserId
from ..stamp_sheet.VerifySubscribeRankingScoreByUserId import VerifySubscribeRankingScoreByUserId


class NamespaceRef:
    namespace_name: str

    def __init__(
        self,
        namespace_name: str,
    ):
        self.namespace_name = namespace_name

    def global_ranking_model(
        self,
        ranking_name: str,
    ) -> GlobalRankingModelRef:
        return GlobalRankingModelRef(
            self.namespace_name,
            ranking_name,
        )

    def subscribe_ranking_model(
        self,
        ranking_name: str,
    ) -> SubscribeRankingModelRef:
        return SubscribeRankingModelRef(
            self.namespace_name,
            ranking_name,
        )

    def cluster_ranking_model(
        self,
        ranking_name: str,
    ) -> ClusterRankingModelRef:
        return ClusterRankingModelRef(
            self.namespace_name,
            ranking_name,
        )

    def create_global_ranking_received_reward(
        self,
        ranking_name: str,
        season: Optional[int] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> CreateGlobalRankingReceivedRewardByUserId:
        return CreateGlobalRankingReceivedRewardByUserId(
            self.namespace_name,
            ranking_name,
            season,
            user_id,
        )

    def create_cluster_ranking_received_reward(
        self,
        ranking_name: str,
        cluster_name: str,
        season: Optional[int] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> CreateClusterRankingReceivedRewardByUserId:
        return CreateClusterRankingReceivedRewardByUserId(
            self.namespace_name,
            ranking_name,
            cluster_name,
            season,
            user_id,
        )

    def verify_global_ranking_score(
        self,
        ranking_name: str,
        verify_type: str,
        score: int,
        season: Optional[int] = None,
        multiply_value_specifying_quantity: Optional[bool] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> VerifyGlobalRankingScoreByUserId:
        return VerifyGlobalRankingScoreByUserId(
            self.namespace_name,
            ranking_name,
            verify_type,
            score,
            season,
            multiply_value_specifying_quantity,
            user_id,
        )

    def verify_cluster_ranking_score(
        self,
        ranking_name: str,
        cluster_name: str,
        verify_type: str,
        score: int,
        season: Optional[int] = None,
        multiply_value_specifying_quantity: Optional[bool] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> VerifyClusterRankingScoreByUserId:
        return VerifyClusterRankingScoreByUserId(
            self.namespace_name,
            ranking_name,
            cluster_name,
            verify_type,
            score,
            season,
            multiply_value_specifying_quantity,
            user_id,
        )

    def verify_subscribe_ranking_score(
        self,
        ranking_name: str,
        verify_type: str,
        score: int,
        season: Optional[int] = None,
        multiply_value_specifying_quantity: Optional[bool] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> VerifySubscribeRankingScoreByUserId:
        return VerifySubscribeRankingScoreByUserId(
            self.namespace_name,
            ranking_name,
            verify_type,
            score,
            season,
            multiply_value_specifying_quantity,
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
                "ranking2",
                self.namespace_name,
            ],
        ).str(
        )
