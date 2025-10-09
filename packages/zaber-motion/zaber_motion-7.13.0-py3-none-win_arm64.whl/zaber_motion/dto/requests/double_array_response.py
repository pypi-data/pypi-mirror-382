# This file is generated. Do not modify by hand.
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass
from dataclasses import dataclass, field
from typing import Any, Dict, List
import decimal
from collections.abc import Iterable
import zaber_bson


@dataclass
class DoubleArrayResponse:

    values: List[float] = field(default_factory=list)

    @staticmethod
    def zero_values() -> 'DoubleArrayResponse':
        return DoubleArrayResponse(
            values=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'DoubleArrayResponse':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return DoubleArrayResponse.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'values': [float(item) for item in self.values] if self.values is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'DoubleArrayResponse':
        return DoubleArrayResponse(
            values=data.get('values'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.values is not None:
            if not isinstance(self.values, Iterable):
                raise ValueError('Property "Values" of "DoubleArrayResponse" is not iterable.')

            for i, values_item in enumerate(self.values):
                if values_item is None:
                    raise ValueError(f'Item {i} in property "Values" of "DoubleArrayResponse" is None.')

                if not isinstance(values_item, (int, float, decimal.Decimal)):
                    raise ValueError(f'Item {i} in property "Values" of "DoubleArrayResponse" is not a number.')
