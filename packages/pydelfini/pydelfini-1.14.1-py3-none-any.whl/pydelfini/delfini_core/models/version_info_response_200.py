from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define


T = TypeVar("T", bound="VersionInfoResponse200")


@_attrs_define
class VersionInfoResponse200:
    """VersionInfoResponse200 model

    Attributes:
        scheme (str):
        server_name (str):
        version (str):
    """

    scheme: str
    server_name: str
    version: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        scheme = self.scheme
        server_name = self.server_name
        version = self.version

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "scheme": scheme,
                "server_name": server_name,
                "version": version,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`VersionInfoResponse200` from a dict"""
        d = src_dict.copy()
        scheme = d.pop("scheme")

        server_name = d.pop("server_name")

        version = d.pop("version")

        version_info_response_200 = cls(
            scheme=scheme,
            server_name=server_name,
            version=version,
        )

        return version_info_response_200
