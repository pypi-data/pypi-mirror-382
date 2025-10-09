# This file is generated. Do not modify by hand.
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson


@dataclass
class TriggerEmptyRequest:

    interface_id: int = 0

    device: int = 0

    trigger_number: int = 0

    @staticmethod
    def zero_values() -> 'TriggerEmptyRequest':
        return TriggerEmptyRequest(
            interface_id=0,
            device=0,
            trigger_number=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'TriggerEmptyRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return TriggerEmptyRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'triggerNumber': int(self.trigger_number),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'TriggerEmptyRequest':
        return TriggerEmptyRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            trigger_number=data.get('triggerNumber'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "TriggerEmptyRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "TriggerEmptyRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "TriggerEmptyRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "TriggerEmptyRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "TriggerEmptyRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "TriggerEmptyRequest" is not integer value.')

        if self.trigger_number is None:
            raise ValueError(f'Property "TriggerNumber" of "TriggerEmptyRequest" is None.')

        if not isinstance(self.trigger_number, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "TriggerNumber" of "TriggerEmptyRequest" is not a number.')

        if int(self.trigger_number) != self.trigger_number:
            raise ValueError(f'Property "TriggerNumber" of "TriggerEmptyRequest" is not integer value.')
