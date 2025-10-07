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
from .GlobalMessageRef import GlobalMessageRef
from ..stamp_sheet.SendMessageByUserId import SendMessageByUserId
from ...core.model import AcquireAction
from ..model.TimeSpan import TimeSpan
from ..stamp_sheet.OpenMessageByUserId import OpenMessageByUserId
from ..stamp_sheet.DeleteMessageByUserId import DeleteMessageByUserId


class NamespaceRef:
    namespace_name: str

    def __init__(
        self,
        namespace_name: str,
    ):
        self.namespace_name = namespace_name

    def global_message(
        self,
        global_message_name: str,
    ) -> GlobalMessageRef:
        return GlobalMessageRef(
            self.namespace_name,
            global_message_name,
        )

    def send_message(
        self,
        metadata: str,
        read_acquire_actions: Optional[List[AcquireAction]] = None,
        expires_at: Optional[int] = None,
        expires_time_span: Optional[TimeSpan] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> SendMessageByUserId:
        return SendMessageByUserId(
            self.namespace_name,
            metadata,
            read_acquire_actions,
            expires_at,
            expires_time_span,
            user_id,
        )

    def open_message(
        self,
        message_name: Optional[str] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> OpenMessageByUserId:
        return OpenMessageByUserId(
            self.namespace_name,
            message_name,
            user_id,
        )

    def delete_message(
        self,
        message_name: Optional[str] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> DeleteMessageByUserId:
        return DeleteMessageByUserId(
            self.namespace_name,
            message_name,
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
                "inbox",
                self.namespace_name,
            ],
        ).str(
        )
