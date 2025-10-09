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

from ...core.model import CdkResource, Stack
from ...core.func import GetAttr

from ..ref.NamespaceRef import NamespaceRef
from .enums.NamespaceType import NamespaceType
from .enums.NamespaceFirehoseCompressData import NamespaceFirehoseCompressData

from .options.NamespaceOptions import NamespaceOptions


class Namespace(CdkResource):
    stack: Stack
    name: str
    description: Optional[str] = None
    type: Optional[NamespaceType] = None
    gcp_credential_json: Optional[str] = None
    big_query_dataset_name: Optional[str] = None
    log_expire_days: Optional[int] = None
    aws_region: Optional[str] = None
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    firehose_stream_name: Optional[str] = None
    firehose_compress_data: Optional[NamespaceFirehoseCompressData] = None

    def __init__(
        self,
        stack: Stack,
        name: str,
        options: Optional[NamespaceOptions] = NamespaceOptions(),
    ):
        super().__init__(
            "Log_Namespace_" + name
        )

        self.stack = stack
        self.name = name
        self.description = options.description if options.description else None
        self.type = options.type if options.type else None
        self.gcp_credential_json = options.gcp_credential_json if options.gcp_credential_json else None
        self.big_query_dataset_name = options.big_query_dataset_name if options.big_query_dataset_name else None
        self.log_expire_days = options.log_expire_days if options.log_expire_days else None
        self.aws_region = options.aws_region if options.aws_region else None
        self.aws_access_key_id = options.aws_access_key_id if options.aws_access_key_id else None
        self.aws_secret_access_key = options.aws_secret_access_key if options.aws_secret_access_key else None
        self.firehose_stream_name = options.firehose_stream_name if options.firehose_stream_name else None
        self.firehose_compress_data = options.firehose_compress_data if options.firehose_compress_data else None
        stack.add_resource(
            self,
        )


    def alternate_keys(
        self,
    ):
        return "name"

    def resource_type(
        self,
    ) -> str:
        return "GS2::Log::Namespace"

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.name is not None:
            properties["Name"] = self.name
        if self.description is not None:
            properties["Description"] = self.description
        if self.type is not None:
            properties["Type"] = self.type
        if self.gcp_credential_json is not None:
            properties["GcpCredentialJson"] = self.gcp_credential_json
        if self.big_query_dataset_name is not None:
            properties["BigQueryDatasetName"] = self.big_query_dataset_name
        if self.log_expire_days is not None:
            properties["LogExpireDays"] = self.log_expire_days
        if self.aws_region is not None:
            properties["AwsRegion"] = self.aws_region
        if self.aws_access_key_id is not None:
            properties["AwsAccessKeyId"] = self.aws_access_key_id
        if self.aws_secret_access_key is not None:
            properties["AwsSecretAccessKey"] = self.aws_secret_access_key
        if self.firehose_stream_name is not None:
            properties["FirehoseStreamName"] = self.firehose_stream_name
        if self.firehose_compress_data is not None:
            properties["FirehoseCompressData"] = self.firehose_compress_data

        return properties

    def ref(
        self,
    ) -> NamespaceRef:
        return NamespaceRef(
            self.name,
        )

    def get_attr_namespace_id(
        self,
    ) -> GetAttr:
        return GetAttr(
            self,
            "Item.NamespaceId",
            None,
        )
