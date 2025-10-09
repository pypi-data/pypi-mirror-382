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
from .options.AppleAppStoreSubscriptionContentOptions import AppleAppStoreSubscriptionContentOptions


class AppleAppStoreSubscriptionContent:
    subscription_group_identifier: Optional[str] = None

    def __init__(
        self,
        options: Optional[AppleAppStoreSubscriptionContentOptions] = AppleAppStoreSubscriptionContentOptions(),
    ):
        self.subscription_group_identifier = options.subscription_group_identifier if options.subscription_group_identifier else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.subscription_group_identifier is not None:
            properties["subscriptionGroupIdentifier"] = self.subscription_group_identifier

        return properties
