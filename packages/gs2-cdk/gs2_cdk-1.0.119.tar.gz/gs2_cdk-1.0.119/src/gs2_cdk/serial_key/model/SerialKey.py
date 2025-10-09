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
from .options.SerialKeyOptions import SerialKeyOptions
from .options.SerialKeyStatusIsActiveOptions import SerialKeyStatusIsActiveOptions
from .options.SerialKeyStatusIsUsedOptions import SerialKeyStatusIsUsedOptions
from .options.SerialKeyStatusIsInactiveOptions import SerialKeyStatusIsInactiveOptions
from .enums.SerialKeyStatus import SerialKeyStatus


class SerialKey:
    campaign_model_name: str
    code: str
    status: SerialKeyStatus
    created_at: int
    updated_at: int
    metadata: Optional[str] = None
    used_user_id: Optional[str] = None
    used_at: Optional[int] = None

    def __init__(
        self,
        campaign_model_name: str,
        code: str,
        status: SerialKeyStatus,
        created_at: int,
        updated_at: int,
        options: Optional[SerialKeyOptions] = SerialKeyOptions(),
    ):
        self.campaign_model_name = campaign_model_name
        self.code = code
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at
        self.metadata = options.metadata if options.metadata else None
        self.used_user_id = options.used_user_id if options.used_user_id else None
        self.used_at = options.used_at if options.used_at else None

    @staticmethod
    def status_is_active(
        campaign_model_name: str,
        code: str,
        created_at: int,
        updated_at: int,
        options: Optional[SerialKeyStatusIsActiveOptions] = SerialKeyStatusIsActiveOptions(),
    ) -> SerialKey:
        return SerialKey(
            campaign_model_name,
            code,
            SerialKeyStatus.ACTIVE,
            created_at,
            updated_at,
            SerialKeyOptions(
                options.metadata,
                options.used_at,
            ),
        )

    @staticmethod
    def status_is_used(
        campaign_model_name: str,
        code: str,
        created_at: int,
        updated_at: int,
        used_user_id: str,
        options: Optional[SerialKeyStatusIsUsedOptions] = SerialKeyStatusIsUsedOptions(),
    ) -> SerialKey:
        return SerialKey(
            campaign_model_name,
            code,
            SerialKeyStatus.USED,
            created_at,
            updated_at,
            SerialKeyOptions(
                used_user_id,
                options.metadata,
                options.used_at,
            ),
        )

    @staticmethod
    def status_is_inactive(
        campaign_model_name: str,
        code: str,
        created_at: int,
        updated_at: int,
        options: Optional[SerialKeyStatusIsInactiveOptions] = SerialKeyStatusIsInactiveOptions(),
    ) -> SerialKey:
        return SerialKey(
            campaign_model_name,
            code,
            SerialKeyStatus.INACTIVE,
            created_at,
            updated_at,
            SerialKeyOptions(
                options.metadata,
                options.used_at,
            ),
        )

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.campaign_model_name is not None:
            properties["campaignModelName"] = self.campaign_model_name
        if self.code is not None:
            properties["code"] = self.code
        if self.metadata is not None:
            properties["metadata"] = self.metadata
        if self.status is not None:
            properties["status"] = self.status.value
        if self.used_user_id is not None:
            properties["usedUserId"] = self.used_user_id
        if self.created_at is not None:
            properties["createdAt"] = self.created_at
        if self.used_at is not None:
            properties["usedAt"] = self.used_at
        if self.updated_at is not None:
            properties["updatedAt"] = self.updated_at

        return properties
