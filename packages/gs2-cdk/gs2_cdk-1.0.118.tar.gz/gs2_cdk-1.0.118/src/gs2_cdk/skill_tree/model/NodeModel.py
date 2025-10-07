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
from ...core.model import VerifyAction
from ...core.model import ConsumeAction
from ...core.model import AcquireAction
from .options.NodeModelOptions import NodeModelOptions


class NodeModel:
    name: str
    release_consume_actions: List[ConsumeAction]
    restrain_return_rate: float
    metadata: Optional[str] = None
    release_verify_actions: Optional[List[VerifyAction]] = None
    return_acquire_actions: Optional[List[AcquireAction]] = None
    premise_node_names: Optional[List[str]] = None

    def __init__(
        self,
        name: str,
        release_consume_actions: List[ConsumeAction],
        restrain_return_rate: float,
        options: Optional[NodeModelOptions] = NodeModelOptions(),
    ):
        self.name = name
        self.release_consume_actions = release_consume_actions
        self.restrain_return_rate = restrain_return_rate
        self.metadata = options.metadata if options.metadata else None
        self.release_verify_actions = options.release_verify_actions if options.release_verify_actions else None
        self.return_acquire_actions = options.return_acquire_actions if options.return_acquire_actions else None
        self.premise_node_names = options.premise_node_names if options.premise_node_names else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.name is not None:
            properties["name"] = self.name
        if self.metadata is not None:
            properties["metadata"] = self.metadata
        if self.release_verify_actions is not None:
            properties["releaseVerifyActions"] = [
                v.properties(
                )
                for v in self.release_verify_actions
            ]
        if self.release_consume_actions is not None:
            properties["releaseConsumeActions"] = [
                v.properties(
                )
                for v in self.release_consume_actions
            ]
        if self.restrain_return_rate is not None:
            properties["restrainReturnRate"] = self.restrain_return_rate
        if self.premise_node_names is not None:
            properties["premiseNodeNames"] = self.premise_node_names

        return properties
