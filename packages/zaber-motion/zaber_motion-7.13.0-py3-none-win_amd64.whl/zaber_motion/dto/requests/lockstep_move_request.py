# This file is generated. Do not modify by hand.
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson
from .axis_move_type import AxisMoveType
from ...units import Units, UnitsAndLiterals, units_from_literals


@dataclass
class LockstepMoveRequest:

    interface_id: int = 0

    device: int = 0

    lockstep_group_id: int = 0

    wait_until_idle: bool = False

    type: AxisMoveType = next(first for first in AxisMoveType)

    arg: float = 0

    unit: UnitsAndLiterals = Units.NATIVE

    velocity: float = 0

    velocity_unit: UnitsAndLiterals = Units.NATIVE

    acceleration: float = 0

    acceleration_unit: UnitsAndLiterals = Units.NATIVE

    @staticmethod
    def zero_values() -> 'LockstepMoveRequest':
        return LockstepMoveRequest(
            interface_id=0,
            device=0,
            lockstep_group_id=0,
            wait_until_idle=False,
            type=next(first for first in AxisMoveType),
            arg=0,
            unit=Units.NATIVE,
            velocity=0,
            velocity_unit=Units.NATIVE,
            acceleration=0,
            acceleration_unit=Units.NATIVE,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'LockstepMoveRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return LockstepMoveRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'lockstepGroupId': int(self.lockstep_group_id),
            'waitUntilIdle': bool(self.wait_until_idle),
            'type': self.type.value,
            'arg': float(self.arg),
            'unit': units_from_literals(self.unit).value,
            'velocity': float(self.velocity),
            'velocityUnit': units_from_literals(self.velocity_unit).value,
            'acceleration': float(self.acceleration),
            'accelerationUnit': units_from_literals(self.acceleration_unit).value,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'LockstepMoveRequest':
        return LockstepMoveRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            lockstep_group_id=data.get('lockstepGroupId'),  # type: ignore
            wait_until_idle=data.get('waitUntilIdle'),  # type: ignore
            type=AxisMoveType(data.get('type')),  # type: ignore
            arg=data.get('arg'),  # type: ignore
            unit=Units(data.get('unit')),  # type: ignore
            velocity=data.get('velocity'),  # type: ignore
            velocity_unit=Units(data.get('velocityUnit')),  # type: ignore
            acceleration=data.get('acceleration'),  # type: ignore
            acceleration_unit=Units(data.get('accelerationUnit')),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "LockstepMoveRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "LockstepMoveRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "LockstepMoveRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "LockstepMoveRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "LockstepMoveRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "LockstepMoveRequest" is not integer value.')

        if self.lockstep_group_id is None:
            raise ValueError(f'Property "LockstepGroupId" of "LockstepMoveRequest" is None.')

        if not isinstance(self.lockstep_group_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "LockstepGroupId" of "LockstepMoveRequest" is not a number.')

        if int(self.lockstep_group_id) != self.lockstep_group_id:
            raise ValueError(f'Property "LockstepGroupId" of "LockstepMoveRequest" is not integer value.')

        if self.type is None:
            raise ValueError(f'Property "Type" of "LockstepMoveRequest" is None.')

        if not isinstance(self.type, AxisMoveType):
            raise ValueError(f'Property "Type" of "LockstepMoveRequest" is not an instance of "AxisMoveType".')

        if self.arg is None:
            raise ValueError(f'Property "Arg" of "LockstepMoveRequest" is None.')

        if not isinstance(self.arg, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Arg" of "LockstepMoveRequest" is not a number.')

        if self.unit is None:
            raise ValueError(f'Property "Unit" of "LockstepMoveRequest" is None.')

        if not isinstance(self.unit, (Units, str)):
            raise ValueError(f'Property "Unit" of "LockstepMoveRequest" is not Units.')

        if self.velocity is None:
            raise ValueError(f'Property "Velocity" of "LockstepMoveRequest" is None.')

        if not isinstance(self.velocity, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Velocity" of "LockstepMoveRequest" is not a number.')

        if self.velocity_unit is None:
            raise ValueError(f'Property "VelocityUnit" of "LockstepMoveRequest" is None.')

        if not isinstance(self.velocity_unit, (Units, str)):
            raise ValueError(f'Property "VelocityUnit" of "LockstepMoveRequest" is not Units.')

        if self.acceleration is None:
            raise ValueError(f'Property "Acceleration" of "LockstepMoveRequest" is None.')

        if not isinstance(self.acceleration, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Acceleration" of "LockstepMoveRequest" is not a number.')

        if self.acceleration_unit is None:
            raise ValueError(f'Property "AccelerationUnit" of "LockstepMoveRequest" is None.')

        if not isinstance(self.acceleration_unit, (Units, str)):
            raise ValueError(f'Property "AccelerationUnit" of "LockstepMoveRequest" is not Units.')
