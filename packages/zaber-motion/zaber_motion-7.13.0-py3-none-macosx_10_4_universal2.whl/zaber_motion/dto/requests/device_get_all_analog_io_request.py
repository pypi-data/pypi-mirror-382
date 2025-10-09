# This file is generated. Do not modify by hand.
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson


@dataclass
class DeviceGetAllAnalogIORequest:

    interface_id: int = 0

    device: int = 0

    channel_type: str = ""

    @staticmethod
    def zero_values() -> 'DeviceGetAllAnalogIORequest':
        return DeviceGetAllAnalogIORequest(
            interface_id=0,
            device=0,
            channel_type="",
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'DeviceGetAllAnalogIORequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return DeviceGetAllAnalogIORequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'channelType': str(self.channel_type or ''),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'DeviceGetAllAnalogIORequest':
        return DeviceGetAllAnalogIORequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            channel_type=data.get('channelType'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "DeviceGetAllAnalogIORequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "DeviceGetAllAnalogIORequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "DeviceGetAllAnalogIORequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "DeviceGetAllAnalogIORequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "DeviceGetAllAnalogIORequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "DeviceGetAllAnalogIORequest" is not integer value.')

        if self.channel_type is not None:
            if not isinstance(self.channel_type, str):
                raise ValueError(f'Property "ChannelType" of "DeviceGetAllAnalogIORequest" is not a string.')
