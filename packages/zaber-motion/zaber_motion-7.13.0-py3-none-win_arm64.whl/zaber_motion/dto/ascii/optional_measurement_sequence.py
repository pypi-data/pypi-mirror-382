# This file is generated. Do not modify by hand.
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import decimal
from collections.abc import Iterable
import zaber_bson
from ...units import Units, UnitsAndLiterals, units_from_literals


@dataclass
class OptionalMeasurementSequence:
    """
    Represents a sequence of optional numerical values with optional units specified.
    """

    values: List[Optional[float]]
    """
    Sequence of values.
    """

    unit: Optional[UnitsAndLiterals] = None
    """
    Optional units of the sequence.
    """

    @staticmethod
    def zero_values() -> 'OptionalMeasurementSequence':
        return OptionalMeasurementSequence(
            values=[],
            unit=None,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'OptionalMeasurementSequence':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return OptionalMeasurementSequence.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'values': [float(item) if item is not None else None for item in self.values] if self.values is not None else [],
            'unit': units_from_literals(self.unit).value if self.unit is not None else None,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'OptionalMeasurementSequence':
        return OptionalMeasurementSequence(
            values=data.get('values'),  # type: ignore
            unit=Units(data.get('unit')) if data.get('unit') is not None else None,  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.values is not None:
            if not isinstance(self.values, Iterable):
                raise ValueError('Property "Values" of "OptionalMeasurementSequence" is not iterable.')

            for i, values_item in enumerate(self.values):
                if values_item is not None:
                    if not isinstance(values_item, (int, float, decimal.Decimal)):
                        raise ValueError(f'Item {i} in property "Values" of "OptionalMeasurementSequence" is not a number.')

        if self.unit is not None:
            if not isinstance(self.unit, (Units, str)):
                raise ValueError(f'Property "Unit" of "OptionalMeasurementSequence" is not Units.')
