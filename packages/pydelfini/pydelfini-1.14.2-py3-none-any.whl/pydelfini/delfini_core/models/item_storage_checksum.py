from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field


T = TypeVar("T", bound="ItemStorageChecksum")


@_attrs_define
class ItemStorageChecksum:
    """ItemStorageChecksum model"""

    additional_properties: Dict[str, str] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`ItemStorageChecksum` from a dict"""
        d = src_dict.copy()
        item_storage_checksum = cls()

        item_storage_checksum.additional_properties = d
        return item_storage_checksum

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> str:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: str) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
