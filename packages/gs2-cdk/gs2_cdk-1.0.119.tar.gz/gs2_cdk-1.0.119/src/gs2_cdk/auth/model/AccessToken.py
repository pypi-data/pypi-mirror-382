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
from .options.AccessTokenOptions import AccessTokenOptions


class AccessToken:
    owner_id: str
    user_id: str
    real_user_id: str
    expire: int
    time_offset: int
    federation_from_user_id: Optional[str] = None
    federation_policy_document: Optional[str] = None

    def __init__(
        self,
        owner_id: str,
        user_id: str,
        real_user_id: str,
        expire: int,
        time_offset: int,
        options: Optional[AccessTokenOptions] = AccessTokenOptions(),
    ):
        self.owner_id = owner_id
        self.user_id = user_id
        self.real_user_id = real_user_id
        self.expire = expire
        self.time_offset = time_offset
        self.federation_from_user_id = options.federation_from_user_id if options.federation_from_user_id else None
        self.federation_policy_document = options.federation_policy_document if options.federation_policy_document else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.owner_id is not None:
            properties["ownerId"] = self.owner_id
        if self.user_id is not None:
            properties["userId"] = self.user_id
        if self.real_user_id is not None:
            properties["realUserId"] = self.real_user_id
        if self.federation_from_user_id is not None:
            properties["federationFromUserId"] = self.federation_from_user_id
        if self.federation_policy_document is not None:
            properties["federationPolicyDocument"] = self.federation_policy_document
        if self.expire is not None:
            properties["expire"] = self.expire
        if self.time_offset is not None:
            properties["timeOffset"] = self.time_offset

        return properties
