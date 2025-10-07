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
from .options.CampaignModelOptions import CampaignModelOptions


class CampaignModel:
    name: str
    enable_campaign_code: bool
    metadata: Optional[str] = None

    def __init__(
        self,
        name: str,
        enable_campaign_code: bool,
        options: Optional[CampaignModelOptions] = CampaignModelOptions(),
    ):
        self.name = name
        self.enable_campaign_code = enable_campaign_code
        self.metadata = options.metadata if options.metadata else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.name is not None:
            properties["name"] = self.name
        if self.metadata is not None:
            properties["metadata"] = self.metadata
        if self.enable_campaign_code is not None:
            properties["enableCampaignCode"] = self.enable_campaign_code

        return properties
