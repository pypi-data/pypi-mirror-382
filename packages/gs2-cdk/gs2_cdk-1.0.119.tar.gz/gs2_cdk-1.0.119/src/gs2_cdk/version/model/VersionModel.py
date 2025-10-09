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
from .Version import Version
from .ScheduleVersion import ScheduleVersion
from .options.VersionModelOptions import VersionModelOptions
from .options.VersionModelTypeIsSimpleOptions import VersionModelTypeIsSimpleOptions
from .options.VersionModelTypeIsScheduleOptions import VersionModelTypeIsScheduleOptions
from .options.VersionModelScopeIsPassiveOptions import VersionModelScopeIsPassiveOptions
from .options.VersionModelScopeIsActiveOptions import VersionModelScopeIsActiveOptions
from .enums.VersionModelScope import VersionModelScope
from .enums.VersionModelType import VersionModelType
from .enums.VersionModelApproveRequirement import VersionModelApproveRequirement


class VersionModel:
    name: str
    scope: VersionModelScope
    type: VersionModelType
    metadata: Optional[str] = None
    current_version: Optional[Version] = None
    warning_version: Optional[Version] = None
    error_version: Optional[Version] = None
    schedule_versions: Optional[List[ScheduleVersion]] = None
    need_signature: Optional[bool] = None
    signature_key_id: Optional[str] = None
    approve_requirement: Optional[VersionModelApproveRequirement] = None

    def __init__(
        self,
        name: str,
        scope: VersionModelScope,
        type: VersionModelType,
        options: Optional[VersionModelOptions] = VersionModelOptions(),
    ):
        self.name = name
        self.scope = scope
        self.type = type
        self.metadata = options.metadata if options.metadata else None
        self.current_version = options.current_version if options.current_version else None
        self.warning_version = options.warning_version if options.warning_version else None
        self.error_version = options.error_version if options.error_version else None
        self.schedule_versions = options.schedule_versions if options.schedule_versions else None
        self.need_signature = options.need_signature if options.need_signature else None
        self.signature_key_id = options.signature_key_id if options.signature_key_id else None
        self.approve_requirement = options.approve_requirement if options.approve_requirement else None

    @staticmethod
    def type_is_simple(
        name: str,
        scope: VersionModelScope,
        warning_version: Version,
        error_version: Version,
        options: Optional[VersionModelTypeIsSimpleOptions] = VersionModelTypeIsSimpleOptions(),
    ) -> VersionModel:
        return VersionModel(
            name,
            scope,
            VersionModelType.SIMPLE,
            VersionModelOptions(
                warning_version,
                error_version,
                options.metadata,
                options.schedule_versions,
            ),
        )

    @staticmethod
    def type_is_schedule(
        name: str,
        scope: VersionModelScope,
        options: Optional[VersionModelTypeIsScheduleOptions] = VersionModelTypeIsScheduleOptions(),
    ) -> VersionModel:
        return VersionModel(
            name,
            scope,
            VersionModelType.SCHEDULE,
            VersionModelOptions(
                options.metadata,
                options.schedule_versions,
            ),
        )

    @staticmethod
    def scope_is_passive(
        name: str,
        type: VersionModelType,
        need_signature: bool,
        options: Optional[VersionModelScopeIsPassiveOptions] = VersionModelScopeIsPassiveOptions(),
    ) -> VersionModel:
        return VersionModel(
            name,
            VersionModelScope.PASSIVE,
            type,
            VersionModelOptions(
                need_signature,
                options.metadata,
                options.schedule_versions,
            ),
        )

    @staticmethod
    def scope_is_active(
        name: str,
        type: VersionModelType,
        approve_requirement: VersionModelApproveRequirement,
        options: Optional[VersionModelScopeIsActiveOptions] = VersionModelScopeIsActiveOptions(),
    ) -> VersionModel:
        return VersionModel(
            name,
            VersionModelScope.ACTIVE,
            type,
            VersionModelOptions(
                approve_requirement,
                options.metadata,
                options.schedule_versions,
            ),
        )

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.name is not None:
            properties["name"] = self.name
        if self.metadata is not None:
            properties["metadata"] = self.metadata
        if self.scope is not None:
            properties["scope"] = self.scope.value
        if self.type is not None:
            properties["type"] = self.type.value
        if self.current_version is not None:
            properties["currentVersion"] = self.current_version.properties(
            )
        if self.warning_version is not None:
            properties["warningVersion"] = self.warning_version.properties(
            )
        if self.error_version is not None:
            properties["errorVersion"] = self.error_version.properties(
            )
        if self.schedule_versions is not None:
            properties["scheduleVersions"] = [
                v.properties(
                )
                for v in self.schedule_versions
            ]
        if self.need_signature is not None:
            properties["needSignature"] = self.need_signature
        if self.signature_key_id is not None:
            properties["signatureKeyId"] = self.signature_key_id
        if self.approve_requirement is not None:
            properties["approveRequirement"] = self.approve_requirement.value

        return properties
