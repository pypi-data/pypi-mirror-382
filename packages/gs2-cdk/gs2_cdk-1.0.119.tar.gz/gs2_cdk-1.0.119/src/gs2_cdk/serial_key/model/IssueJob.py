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
from .options.IssueJobOptions import IssueJobOptions
from .enums.IssueJobStatus import IssueJobStatus


class IssueJob:
    name: str
    issued_count: int
    issue_request_count: int
    status: IssueJobStatus
    metadata: Optional[str] = None
    revision: Optional[int] = None

    def __init__(
        self,
        name: str,
        issued_count: int,
        issue_request_count: int,
        status: IssueJobStatus,
        options: Optional[IssueJobOptions] = IssueJobOptions(),
    ):
        self.name = name
        self.issued_count = issued_count
        self.issue_request_count = issue_request_count
        self.status = status
        self.metadata = options.metadata if options.metadata else None
        self.revision = options.revision if options.revision else None

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.name is not None:
            properties["name"] = self.name
        if self.metadata is not None:
            properties["metadata"] = self.metadata
        if self.issued_count is not None:
            properties["issuedCount"] = self.issued_count
        if self.issue_request_count is not None:
            properties["issueRequestCount"] = self.issue_request_count
        if self.status is not None:
            properties["status"] = self.status.value

        return properties
