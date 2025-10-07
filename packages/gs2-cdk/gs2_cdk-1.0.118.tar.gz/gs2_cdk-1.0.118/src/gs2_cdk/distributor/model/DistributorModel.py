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
from .options.DistributorModelOptions import DistributorModelOptions


class DistributorModel:
    name: str
    metadata: Optional[str] = None
    inbox_namespace_id: Optional[str] = None
    white_list_target_ids: Optional[List[str]] = None

    def __init__(
        self,
        name: str,
        options: Optional[DistributorModelOptions] = DistributorModelOptions(),
    ):
        self.name = name
        self.metadata = options.metadata if options.metadata else None
        self.inbox_namespace_id = options.inbox_namespace_id if options.inbox_namespace_id else None
        self.white_list_target_ids = options.white_list_target_ids if options.white_list_target_ids else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.name is not None:
            properties["name"] = self.name
        if self.metadata is not None:
            properties["metadata"] = self.metadata
        if self.inbox_namespace_id is not None:
            properties["inboxNamespaceId"] = self.inbox_namespace_id
        if self.white_list_target_ids is not None:
            properties["whiteListTargetIds"] = self.white_list_target_ids

        return properties
