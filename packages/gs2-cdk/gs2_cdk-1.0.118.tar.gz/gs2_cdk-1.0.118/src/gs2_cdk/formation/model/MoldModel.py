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
from .SlotModel import SlotModel
from .FormModel import FormModel
from .options.MoldModelOptions import MoldModelOptions


class MoldModel:
    name: str
    initial_max_capacity: int
    max_capacity: int
    form_model: FormModel
    metadata: Optional[str] = None

    def __init__(
        self,
        name: str,
        initial_max_capacity: int,
        max_capacity: int,
        form_model: FormModel,
        options: Optional[MoldModelOptions] = MoldModelOptions(),
    ):
        self.name = name
        self.initial_max_capacity = initial_max_capacity
        self.max_capacity = max_capacity
        self.form_model = form_model
        self.metadata = options.metadata if options.metadata else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.name is not None:
            properties["name"] = self.name
        if self.metadata is not None:
            properties["metadata"] = self.metadata
        if self.initial_max_capacity is not None:
            properties["initialMaxCapacity"] = self.initial_max_capacity
        if self.max_capacity is not None:
            properties["maxCapacity"] = self.max_capacity
        if self.form_model is not None:
            properties["formModel"] = self.form_model.properties(
            )

        return properties
