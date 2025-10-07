from __future__ import annotations
from typing import List


class Func:
    pass


class GetAttr(Func):

    key: str

    def __init__(
            self,
            resource: 'gs2_cdk.CdkResource' = None,
            path: str = None,
            key: str = None
    ):
        if key is None:
            self.key = "{}.{}".format(
                resource.resource_name,
                path,
            )
        else:
            self.key = key

    def str(self) -> str:
        return "!GetAttr {}".format(
            self.key,
        )

    @staticmethod
    def region() -> GetAttr:
        return GetAttr(
            key="Gs2::Region",
        )

    @staticmethod
    def owner_id() -> GetAttr:
        return GetAttr(
            key="Gs2::OwnerId",
        )


class Join(Func):

    separator: str
    values: List[str]

    def __init__(
            self,
            separator: str,
            values: List[str],
    ):
        self.separator = separator
        self.values = values

    def str(self) -> str:
        return "!Join ['{}', [{}]]".format(
            self.separator,
            ', '.join([
                "'{}'".format(value)
                for value in self.values
            ]),
        )
