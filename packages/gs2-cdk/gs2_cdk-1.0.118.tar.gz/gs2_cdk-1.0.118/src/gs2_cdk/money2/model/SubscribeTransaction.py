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
from .options.SubscribeTransactionOptions import SubscribeTransactionOptions
from .enums.SubscribeTransactionStore import SubscribeTransactionStore
from .enums.SubscribeTransactionStatusDetail import SubscribeTransactionStatusDetail


class SubscribeTransaction:
    content_name: str
    transaction_id: str
    store: SubscribeTransactionStore
    status_detail: SubscribeTransactionStatusDetail
    expires_at: int
    user_id: Optional[str] = None
    last_allocated_at: Optional[int] = None
    last_take_over_at: Optional[int] = None
    revision: Optional[int] = None

    def __init__(
        self,
        content_name: str,
        transaction_id: str,
        store: SubscribeTransactionStore,
        status_detail: SubscribeTransactionStatusDetail,
        expires_at: int,
        options: Optional[SubscribeTransactionOptions] = SubscribeTransactionOptions(),
    ):
        self.content_name = content_name
        self.transaction_id = transaction_id
        self.store = store
        self.status_detail = status_detail
        self.expires_at = expires_at
        self.user_id = options.user_id if options.user_id else None
        self.last_allocated_at = options.last_allocated_at if options.last_allocated_at else None
        self.last_take_over_at = options.last_take_over_at if options.last_take_over_at else None
        self.revision = options.revision if options.revision else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.content_name is not None:
            properties["contentName"] = self.content_name
        if self.transaction_id is not None:
            properties["transactionId"] = self.transaction_id
        if self.store is not None:
            properties["store"] = self.store.value
        if self.user_id is not None:
            properties["userId"] = self.user_id
        if self.status_detail is not None:
            properties["statusDetail"] = self.status_detail.value
        if self.expires_at is not None:
            properties["expiresAt"] = self.expires_at
        if self.last_allocated_at is not None:
            properties["lastAllocatedAt"] = self.last_allocated_at
        if self.last_take_over_at is not None:
            properties["lastTakeOverAt"] = self.last_take_over_at

        return properties
