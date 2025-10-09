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
from .CampaignModelRef import CampaignModelRef
from ..stamp_sheet.RevertUseByUserId import RevertUseByUserId
from ..stamp_sheet.IssueOnce import IssueOnce
from ..stamp_sheet.UseByUserId import UseByUserId
from ..stamp_sheet.VerifyCodeByUserId import VerifyCodeByUserId


class NamespaceRef:
    namespace_name: str

    def __init__(
        self,
        namespace_name: str,
    ):
        self.namespace_name = namespace_name

    def campaign_model(
        self,
        campaign_model_name: str,
    ) -> CampaignModelRef:
        return CampaignModelRef(
            self.namespace_name,
            campaign_model_name,
        )

    def revert_use(
        self,
        code: str,
        user_id: Optional[str] = "#{userId}",
    ) -> RevertUseByUserId:
        return RevertUseByUserId(
            self.namespace_name,
            code,
            user_id,
        )

    def issue_once(
        self,
        campaign_model_name: str,
        metadata: Optional[str] = None,
    ) -> IssueOnce:
        return IssueOnce(
            self.namespace_name,
            campaign_model_name,
            metadata,
        )

    def use(
        self,
        code: str,
        user_id: Optional[str] = "#{userId}",
    ) -> UseByUserId:
        return UseByUserId(
            self.namespace_name,
            code,
            user_id,
        )

    def verify_code(
        self,
        code: str,
        verify_type: str,
        campaign_model_name: Optional[str] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> VerifyCodeByUserId:
        return VerifyCodeByUserId(
            self.namespace_name,
            code,
            verify_type,
            campaign_model_name,
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
                "serialKey",
                self.namespace_name,
            ],
        ).str(
        )
