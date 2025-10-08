from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.system_configuration_motd_additional_property_level import (
    SystemConfigurationMotdAdditionalPropertyLevel,
)


T = TypeVar("T", bound="SystemConfigurationMotdAdditionalProperty")


@_attrs_define
class SystemConfigurationMotdAdditionalProperty:
    """SystemConfigurationMotdAdditionalProperty model

    Attributes:
        level (SystemConfigurationMotdAdditionalPropertyLevel):
        message (str):
    """

    level: SystemConfigurationMotdAdditionalPropertyLevel
    message: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        level = self.level.value
        message = self.message

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "level": level,
                "message": message,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`SystemConfigurationMotdAdditionalProperty` from a dict"""
        d = src_dict.copy()
        level = SystemConfigurationMotdAdditionalPropertyLevel(d.pop("level"))

        message = d.pop("message")

        system_configuration_motd_additional_property = cls(
            level=level,
            message=message,
        )

        system_configuration_motd_additional_property.additional_properties = d
        return system_configuration_motd_additional_property

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
