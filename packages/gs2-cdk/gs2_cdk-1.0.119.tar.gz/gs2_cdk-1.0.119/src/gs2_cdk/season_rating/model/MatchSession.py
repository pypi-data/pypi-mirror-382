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

from ..ref.MatchSessionRef import MatchSessionRef

from .options.MatchSessionOptions import MatchSessionOptions


class MatchSession(CdkResource):
    stack: Stack
    namespace_name: str
    session_name: Optional[str] = None
    ttl_seconds: Optional[int] = None

    def __init__(
        self,
        stack: Stack,
        namespace_name: str,
        options: Optional[MatchSessionOptions] = MatchSessionOptions(),
    ):
        super().__init__(
            "SeasonRating_MatchSession_" + name
        )

        self.stack = stack
        self.namespace_name = namespace_name
        self.session_name = options.session_name if options.session_name else None
        self.ttl_seconds = options.ttl_seconds if options.ttl_seconds else None
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
        return "GS2::SeasonRating::MatchSession"

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.namespace_name is not None:
            properties["NamespaceName"] = self.namespace_name
        if self.session_name is not None:
            properties["SessionName"] = self.session_name
        if self.ttl_seconds is not None:
            properties["TtlSeconds"] = self.ttl_seconds

        return properties

    def ref(
        self,
        name: str,
    ) -> MatchSessionRef:
        return MatchSessionRef(
            self.namespace_name,
            name,
        )

    def get_attr_session_id(
        self,
    ) -> GetAttr:
        return GetAttr(
            self,
            "Item.SessionId",
            None,
        )
