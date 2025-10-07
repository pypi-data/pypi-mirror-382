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
from .EntryModelRef import EntryModelRef
from ..stamp_sheet.AddEntriesByUserId import AddEntriesByUserId
from ..stamp_sheet.DeleteEntriesByUserId import DeleteEntriesByUserId
from ..stamp_sheet.VerifyEntryByUserId import VerifyEntryByUserId


class NamespaceRef:
    namespace_name: str

    def __init__(
        self,
        namespace_name: str,
    ):
        self.namespace_name = namespace_name

    def entry_model(
        self,
        entry_model_name: str,
    ) -> EntryModelRef:
        return EntryModelRef(
            self.namespace_name,
            entry_model_name,
        )

    def add_entries(
        self,
        entry_model_names: Optional[List[str]] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> AddEntriesByUserId:
        return AddEntriesByUserId(
            self.namespace_name,
            entry_model_names,
            user_id,
        )

    def delete_entries(
        self,
        entry_model_names: Optional[List[str]] = None,
        user_id: Optional[str] = "#{userId}",
    ) -> DeleteEntriesByUserId:
        return DeleteEntriesByUserId(
            self.namespace_name,
            entry_model_names,
            user_id,
        )

    def verify_entry(
        self,
        entry_model_name: str,
        verify_type: str,
        user_id: Optional[str] = "#{userId}",
    ) -> VerifyEntryByUserId:
        return VerifyEntryByUserId(
            self.namespace_name,
            entry_model_name,
            verify_type,
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
                "dictionary",
                self.namespace_name,
            ],
        ).str(
        )
