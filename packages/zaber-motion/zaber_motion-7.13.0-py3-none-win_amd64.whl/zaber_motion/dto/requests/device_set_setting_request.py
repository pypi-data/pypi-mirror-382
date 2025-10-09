# This file is generated. Do not modify by hand.
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson
from ...units import Units, UnitsAndLiterals, units_from_literals


@dataclass
class DeviceSetSettingRequest:

    interface_id: int = 0

    device: int = 0

    axis: int = 0

    setting: str = ""

    value: float = 0

    unit: UnitsAndLiterals = Units.NATIVE

    @staticmethod
    def zero_values() -> 'DeviceSetSettingRequest':
        return DeviceSetSettingRequest(
            interface_id=0,
            device=0,
            axis=0,
            setting="",
            value=0,
            unit=Units.NATIVE,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'DeviceSetSettingRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return DeviceSetSettingRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'axis': int(self.axis),
            'setting': str(self.setting or ''),
            'value': float(self.value),
            'unit': units_from_literals(self.unit).value,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'DeviceSetSettingRequest':
        return DeviceSetSettingRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            axis=data.get('axis'),  # type: ignore
            setting=data.get('setting'),  # type: ignore
            value=data.get('value'),  # type: ignore
            unit=Units(data.get('unit')),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "DeviceSetSettingRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "DeviceSetSettingRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "DeviceSetSettingRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "DeviceSetSettingRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "DeviceSetSettingRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "DeviceSetSettingRequest" is not integer value.')

        if self.axis is None:
            raise ValueError(f'Property "Axis" of "DeviceSetSettingRequest" is None.')

        if not isinstance(self.axis, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Axis" of "DeviceSetSettingRequest" is not a number.')

        if int(self.axis) != self.axis:
            raise ValueError(f'Property "Axis" of "DeviceSetSettingRequest" is not integer value.')

        if self.setting is not None:
            if not isinstance(self.setting, str):
                raise ValueError(f'Property "Setting" of "DeviceSetSettingRequest" is not a string.')

        if self.value is None:
            raise ValueError(f'Property "Value" of "DeviceSetSettingRequest" is None.')

        if not isinstance(self.value, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Value" of "DeviceSetSettingRequest" is not a number.')

        if self.unit is None:
            raise ValueError(f'Property "Unit" of "DeviceSetSettingRequest" is None.')

        if not isinstance(self.unit, (Units, str)):
            raise ValueError(f'Property "Unit" of "DeviceSetSettingRequest" is not Units.')
