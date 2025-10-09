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
from .Identifier import Identifier
from .AttachSecurityPolicy import AttachSecurityPolicy
from .SecurityPolicy import SecurityPolicy

from ..ref.UserRef import UserRef

from .options.UserOptions import UserOptions


class User(CdkResource):
    stack: Stack
    name: str
    description: Optional[str] = None

    def __init__(
        self,
        stack: Stack,
        name: str,
        options: Optional[UserOptions] = UserOptions(),
    ):
        super().__init__(
            "Identifier_User_" + name
        )

        self.stack = stack
        self.name = name
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
        return "GS2::Identifier::User"

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.name is not None:
            properties["Name"] = self.name
        if self.description is not None:
            properties["Description"] = self.description

        return properties

    def ref(
        self,
    ) -> UserRef:
        return UserRef(
            self.name,
        )


    def attach(
        self,
        security_policy: SecurityPolicy,
    ) -> User:
        AttachSecurityPolicy(
            self.stack,
            self.name,
            security_policy.get_attr_security_policy_id(
            ).str(
            ),
        ).add_depends_on(
            self,
        ).add_depends_on(
            security_policy,
        )

        return self

    def attach_grn(
        self,
        security_policy_grn: str,
    ) -> User:
        AttachSecurityPolicy(
            self.stack,
            self.name,
            security_policy_grn,
        ).add_depends_on(
            self,
        )

        return self

    def identifier(
        self,
    ) -> Identifier:
        identifier =Identifier(
            self.stack,
            self.name,
        );
        identifier.add_depends_on(
            self,
        )

        return identifier

    def get_attr_user_id(
        self,
    ) -> GetAttr:
        return GetAttr(
            self,
            "Item.UserId",
            None,
        )
