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
from .Content import Content
from .options.ViewOptions import ViewOptions


class View:
    contents: Optional[List[Content]] = None
    remove_contents: Optional[List[Content]] = None

    def __init__(
        self,
        options: Optional[ViewOptions] = ViewOptions(),
    ):
        self.contents = options.contents if options.contents else None
        self.remove_contents = options.remove_contents if options.remove_contents else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.contents is not None:
            properties["contents"] = [
                v.properties(
                )
                for v in self.contents
            ]
        if self.remove_contents is not None:
            properties["removeContents"] = [
                v.properties(
                )
                for v in self.remove_contents
            ]

        return properties
