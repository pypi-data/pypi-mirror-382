# This file is generated. Do not modify by hand.
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass
from dataclasses import dataclass, field
from typing import Any, Dict, List
import decimal
from collections.abc import Iterable
import zaber_bson
from ..ascii.stream_axis_definition import StreamAxisDefinition
from ..ascii.pvt_axis_definition import PvtAxisDefinition


@dataclass
class StreamSetupLiveCompositeRequest:

    interface_id: int = 0

    device: int = 0

    stream_id: int = 0

    pvt: bool = False

    axes: List[StreamAxisDefinition] = field(default_factory=list)

    pvt_axes: List[PvtAxisDefinition] = field(default_factory=list)

    @staticmethod
    def zero_values() -> 'StreamSetupLiveCompositeRequest':
        return StreamSetupLiveCompositeRequest(
            interface_id=0,
            device=0,
            stream_id=0,
            pvt=False,
            axes=[],
            pvt_axes=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'StreamSetupLiveCompositeRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return StreamSetupLiveCompositeRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'streamId': int(self.stream_id),
            'pvt': bool(self.pvt),
            'axes': [item.to_dict() for item in self.axes] if self.axes is not None else [],
            'pvtAxes': [item.to_dict() for item in self.pvt_axes] if self.pvt_axes is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'StreamSetupLiveCompositeRequest':
        return StreamSetupLiveCompositeRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            stream_id=data.get('streamId'),  # type: ignore
            pvt=data.get('pvt'),  # type: ignore
            axes=[StreamAxisDefinition.from_dict(item) for item in data.get('axes')],  # type: ignore
            pvt_axes=[PvtAxisDefinition.from_dict(item) for item in data.get('pvtAxes')],  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "StreamSetupLiveCompositeRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "StreamSetupLiveCompositeRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "StreamSetupLiveCompositeRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "StreamSetupLiveCompositeRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "StreamSetupLiveCompositeRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "StreamSetupLiveCompositeRequest" is not integer value.')

        if self.stream_id is None:
            raise ValueError(f'Property "StreamId" of "StreamSetupLiveCompositeRequest" is None.')

        if not isinstance(self.stream_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "StreamId" of "StreamSetupLiveCompositeRequest" is not a number.')

        if int(self.stream_id) != self.stream_id:
            raise ValueError(f'Property "StreamId" of "StreamSetupLiveCompositeRequest" is not integer value.')

        if self.axes is not None:
            if not isinstance(self.axes, Iterable):
                raise ValueError('Property "Axes" of "StreamSetupLiveCompositeRequest" is not iterable.')

            for i, axes_item in enumerate(self.axes):
                if axes_item is None:
                    raise ValueError(f'Item {i} in property "Axes" of "StreamSetupLiveCompositeRequest" is None.')

                if not isinstance(axes_item, StreamAxisDefinition):
                    raise ValueError(f'Item {i} in property "Axes" of "StreamSetupLiveCompositeRequest" is not an instance of "StreamAxisDefinition".')

                axes_item.validate()

        if self.pvt_axes is not None:
            if not isinstance(self.pvt_axes, Iterable):
                raise ValueError('Property "PvtAxes" of "StreamSetupLiveCompositeRequest" is not iterable.')

            for i, pvt_axes_item in enumerate(self.pvt_axes):
                if pvt_axes_item is None:
                    raise ValueError(f'Item {i} in property "PvtAxes" of "StreamSetupLiveCompositeRequest" is None.')

                if not isinstance(pvt_axes_item, PvtAxisDefinition):
                    raise ValueError(f'Item {i} in property "PvtAxes" of "StreamSetupLiveCompositeRequest" is not an instance of "PvtAxisDefinition".')

                pvt_axes_item.validate()
