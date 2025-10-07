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
from ...core.func import GetAttr
from .Policy import Policy

from ..ref.SecurityPolicyRef import SecurityPolicyRef

from .options.SecurityPolicyOptions import SecurityPolicyOptions


class SecurityPolicy(CdkResource):
    stack: Stack
    name: str
    policy: Policy
    description: Optional[str] = None

    def __init__(
        self,
        stack: Stack,
        name: str,
        policy: Policy,
        options: Optional[SecurityPolicyOptions] = SecurityPolicyOptions(),
    ):
        super().__init__(
            "Identifier_SecurityPolicy_" + name
        )

        self.stack = stack
        self.name = name
        self.policy = policy
        self.description = options.description if options.description else None
        stack.add_resource(
            self,
        )


    def alternate_keys(
        self,
    ):
        return "name"

    def resource_type(
        self,
    ) -> str:
        return "GS2::Identifier::SecurityPolicy"

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.name is not None:
            properties["Name"] = self.name
        if self.description is not None:
            properties["Description"] = self.description
        if self.policy is not None:
            properties["Policy"] = self.policy.properties(
            )

        return properties

    def ref(
        self,
    ) -> SecurityPolicyRef:
        return SecurityPolicyRef(
            self.name,
        )
    @staticmethod
    def application_access_grn(
    ) -> str:
        return "grn:gs2::system:identifier:securityPolicy:ApplicationAccess"

    def get_attr_security_policy_id(
        self,
    ) -> GetAttr:
        return GetAttr(
            self,
            "Item.SecurityPolicyId",
            None,
        )
