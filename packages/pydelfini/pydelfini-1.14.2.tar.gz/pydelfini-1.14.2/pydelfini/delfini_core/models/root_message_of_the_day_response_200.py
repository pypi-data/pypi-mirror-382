from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define

from ..models.motd import Motd


T = TypeVar("T", bound="RootMessageOfTheDayResponse200")


@_attrs_define
class RootMessageOfTheDayResponse200:
    """RootMessageOfTheDayResponse200 model

    Attributes:
        messages (List['Motd']):
    """

    messages: List["Motd"]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        messages = []
        for messages_item_data in self.messages:
            messages_item = messages_item_data.to_dict()
            messages.append(messages_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "messages": messages,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`RootMessageOfTheDayResponse200` from a dict"""
        d = src_dict.copy()
        messages = []
        _messages = d.pop("messages")
        for messages_item_data in _messages:
            messages_item = Motd.from_dict(messages_item_data)

            messages.append(messages_item)

        root_message_of_the_day_response_200 = cls(
            messages=messages,
        )

        return root_message_of_the_day_response_200
