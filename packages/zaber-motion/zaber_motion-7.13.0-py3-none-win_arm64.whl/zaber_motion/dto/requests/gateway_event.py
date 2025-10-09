# This file is generated. Do not modify by hand.
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass
from dataclasses import dataclass
from typing import Any, Dict
import zaber_bson


@dataclass
class GatewayEvent:

    event: str = ""

    @staticmethod
    def zero_values() -> 'GatewayEvent':
        return GatewayEvent(
            event="",
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'GatewayEvent':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return GatewayEvent.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'event': str(self.event or ''),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'GatewayEvent':
        return GatewayEvent(
            event=data.get('event'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.event is not None:
            if not isinstance(self.event, str):
                raise ValueError(f'Property "Event" of "GatewayEvent" is not a string.')
