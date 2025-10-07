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
from .options.AppLovinMaxOptions import AppLovinMaxOptions


class AppLovinMax:
    allow_ad_unit_id: str
    event_key: str

    def __init__(
        self,
        allow_ad_unit_id: str,
        event_key: str,
        options: Optional[AppLovinMaxOptions] = AppLovinMaxOptions(),
    ):
        self.allow_ad_unit_id = allow_ad_unit_id
        self.event_key = event_key

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.allow_ad_unit_id is not None:
            properties["allowAdUnitId"] = self.allow_ad_unit_id
        if self.event_key is not None:
            properties["eventKey"] = self.event_key

        return properties
