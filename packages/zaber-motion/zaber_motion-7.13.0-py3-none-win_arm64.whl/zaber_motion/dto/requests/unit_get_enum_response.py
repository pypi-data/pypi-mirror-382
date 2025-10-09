# This file is generated. Do not modify by hand.
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass
from dataclasses import dataclass
from typing import Any, Dict
import zaber_bson
from ...units import Units, UnitsAndLiterals, units_from_literals


@dataclass
class UnitGetEnumResponse:

    unit: UnitsAndLiterals = Units.NATIVE

    @staticmethod
    def zero_values() -> 'UnitGetEnumResponse':
        return UnitGetEnumResponse(
            unit=Units.NATIVE,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'UnitGetEnumResponse':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return UnitGetEnumResponse.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'unit': units_from_literals(self.unit).value,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'UnitGetEnumResponse':
        return UnitGetEnumResponse(
            unit=Units(data.get('unit')),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.unit is None:
            raise ValueError(f'Property "Unit" of "UnitGetEnumResponse" is None.')

        if not isinstance(self.unit, (Units, str)):
            raise ValueError(f'Property "Unit" of "UnitGetEnumResponse" is not Units.')
