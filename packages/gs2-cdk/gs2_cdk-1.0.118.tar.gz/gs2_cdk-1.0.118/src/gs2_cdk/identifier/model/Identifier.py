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
#
# deny overwrite

from __future__ import annotations
from typing import *

from .AttachGuard import AttachGuard
from ...core.model import CdkResource, Stack
from ...core.func import GetAttr

from ..ref.IdentifierRef import IdentifierRef

from .options.IdentifierOptions import IdentifierOptions
from ...guard import Namespace


class Identifier(CdkResource):
    stack: Stack
    user_name: str

    def __init__(
        self,
        stack: Stack,
        user_name: str,
        options: Optional[IdentifierOptions] = IdentifierOptions(),
    ):
        super().__init__(
            "Identifier_Identifier_" + user_name
        )

        self.stack = stack
        self.user_name = user_name
        stack.add_resource(
            self,
        )


    def alternate_keys(
        self,
    ):
        return "userName"

    def resource_type(
        self,
    ) -> str:
        return "GS2::Identifier::Identifier"

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.user_name is not None:
            properties["UserName"] = self.user_name

        return properties

    def ref(
        self,
        client_id: str,
    ) -> IdentifierRef:
        return IdentifierRef(
            self.user_name,
            client_id,
        )

    def attach(
        self,
        guard_namespace: Namespace,
    ) -> Identifier:
        AttachGuard(
            self.stack,
            self.user_name,
            self.get_attr_client_id(
            ).str(
            ),
            guard_namespace.get_attr_namespace_id(
            ).str(
            ),
        ).add_depends_on(
            self,
        ).add_depends_on(
            guard_namespace,
        )

        return self

    def attach_grn(
        self,
        guard_namespace_grn: str,
    ) -> Identifier:
        AttachGuard(
            self.stack,
            self.user_name,
            self.get_attr_client_id(
            ).str(
            ),
            guard_namespace_grn,
        ).add_depends_on(
            self,
        )

        return self

    def get_attr_client_id(
        self,
    ) -> GetAttr:
        return GetAttr(
            self,
            "Item.ClientId",
            None,
        )


    def get_attr_client_secret(
        self,
    ) -> GetAttr:
        return GetAttr(
            self,
            "ClientSecret",
            None,
        )
