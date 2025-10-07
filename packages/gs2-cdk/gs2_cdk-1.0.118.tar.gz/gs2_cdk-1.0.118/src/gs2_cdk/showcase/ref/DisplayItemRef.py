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
from .SalesItemRef import SalesItemRef
from .SalesItemGroupRef import SalesItemGroupRef


class DisplayItemRef:
    namespace_name: str
    display_item_id: str

    def __init__(
        self,
        namespace_name: str,
        display_item_id: str,
    ):
        self.namespace_name = namespace_name
        self.display_item_id = display_item_id

    def sales_item(
        self,
    ) -> SalesItemRef:
        return SalesItemRef(
            self.namespace_name,
            self.display_item_id,
        )

    def sales_item_group(
        self,
    ) -> SalesItemGroupRef:
        return SalesItemGroupRef(
            self.namespace_name,
            self.display_item_id,
        )
