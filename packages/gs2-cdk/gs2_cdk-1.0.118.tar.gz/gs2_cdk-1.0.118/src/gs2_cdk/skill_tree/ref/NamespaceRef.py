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
from .NodeModelRef import NodeModelRef
from ..stamp_sheet.MarkReleaseByUserId import MarkReleaseByUserId
from ..stamp_sheet.MarkRestrainByUserId import MarkRestrainByUserId


class NamespaceRef:
    namespace_name: str

    def __init__(
        self,
        namespace_name: str,
    ):
        self.namespace_name = namespace_name

    def node_model(
        self,
        node_model_name: str,
    ) -> NodeModelRef:
        return NodeModelRef(
            self.namespace_name,
            node_model_name,
        )

    def mark_release(
        self,
        property_id: str,
        node_model_names: List[str],
        user_id: Optional[str] = "#{userId}",
    ) -> MarkReleaseByUserId:
        return MarkReleaseByUserId(
            self.namespace_name,
            property_id,
            node_model_names,
            user_id,
        )

    def mark_restrain(
        self,
        property_id: str,
        node_model_names: List[str],
        user_id: Optional[str] = "#{userId}",
    ) -> MarkRestrainByUserId:
        return MarkRestrainByUserId(
            self.namespace_name,
            property_id,
            node_model_names,
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
                "skillTree",
                self.namespace_name,
            ],
        ).str(
        )
