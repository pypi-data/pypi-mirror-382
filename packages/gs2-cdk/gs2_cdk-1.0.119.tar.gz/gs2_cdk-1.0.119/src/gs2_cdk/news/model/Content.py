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
from .options.ContentOptions import ContentOptions


class Content:
    section: str
    content: str
    front_matter: str

    def __init__(
        self,
        section: str,
        content: str,
        front_matter: str,
        options: Optional[ContentOptions] = ContentOptions(),
    ):
        self.section = section
        self.content = content
        self.front_matter = front_matter

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.section is not None:
            properties["section"] = self.section
        if self.content is not None:
            properties["content"] = self.content
        if self.front_matter is not None:
            properties["frontMatter"] = self.front_matter

        return properties
