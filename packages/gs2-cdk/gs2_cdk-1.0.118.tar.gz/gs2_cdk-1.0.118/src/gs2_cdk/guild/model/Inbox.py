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
from .ReceiveMemberRequest import ReceiveMemberRequest
from .options.InboxOptions import InboxOptions


class Inbox:
    guild_name: str
    from_user_ids: Optional[List[str]] = None
    receive_member_requests: Optional[List[ReceiveMemberRequest]] = None
    revision: Optional[int] = None

    def __init__(
        self,
        guild_name: str,
        options: Optional[InboxOptions] = InboxOptions(),
    ):
        self.guild_name = guild_name
        self.from_user_ids = options.from_user_ids if options.from_user_ids else None
        self.receive_member_requests = options.receive_member_requests if options.receive_member_requests else None
        self.revision = options.revision if options.revision else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.guild_name is not None:
            properties["guildName"] = self.guild_name
        if self.from_user_ids is not None:
            properties["fromUserIds"] = self.from_user_ids
        if self.receive_member_requests is not None:
            properties["receiveMemberRequests"] = [
                v.properties(
                )
                for v in self.receive_member_requests
            ]

        return properties
