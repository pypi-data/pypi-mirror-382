from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.system_configuration_motd_additional_property import (
    SystemConfigurationMotdAdditionalProperty,
)


T = TypeVar("T", bound="SystemConfigurationMotd")


@_attrs_define
class SystemConfigurationMotd:
    """SystemConfigurationMotd model"""

    additional_properties: Dict[
        str, "SystemConfigurationMotdAdditionalProperty"
    ] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""

        field_dict: Dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = prop.to_dict()
        field_dict.update({})

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`SystemConfigurationMotd` from a dict"""
        d = src_dict.copy()
        system_configuration_motd = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = SystemConfigurationMotdAdditionalProperty.from_dict(
                prop_dict
            )

            additional_properties[prop_name] = additional_property

        system_configuration_motd.additional_properties = additional_properties
        return system_configuration_motd

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> "SystemConfigurationMotdAdditionalProperty":
        return self.additional_properties[key]

    def __setitem__(
        self, key: str, value: "SystemConfigurationMotdAdditionalProperty"
    ) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
