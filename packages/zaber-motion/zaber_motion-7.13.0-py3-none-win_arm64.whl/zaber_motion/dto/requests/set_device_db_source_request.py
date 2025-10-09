# This file is generated. Do not modify by hand.
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass
from dataclasses import dataclass
from typing import Any, Dict, Optional
import zaber_bson
from ..device_db_source_type import DeviceDbSourceType


@dataclass
class SetDeviceDbSourceRequest:

    source_type: DeviceDbSourceType = next(first for first in DeviceDbSourceType)
    """
    Whether the source is a web service or a local DB file.
    """

    url_or_file_path: Optional[str] = None
    """
    The URL of the web service or path to the local DB file.
    """

    @staticmethod
    def zero_values() -> 'SetDeviceDbSourceRequest':
        return SetDeviceDbSourceRequest(
            source_type=next(first for first in DeviceDbSourceType),
            url_or_file_path=None,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'SetDeviceDbSourceRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return SetDeviceDbSourceRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'sourceType': self.source_type.value,
            'urlOrFilePath': str(self.url_or_file_path) if self.url_or_file_path is not None else None,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'SetDeviceDbSourceRequest':
        return SetDeviceDbSourceRequest(
            source_type=DeviceDbSourceType(data.get('sourceType')),  # type: ignore
            url_or_file_path=data.get('urlOrFilePath'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.source_type is None:
            raise ValueError(f'Property "SourceType" of "SetDeviceDbSourceRequest" is None.')

        if not isinstance(self.source_type, DeviceDbSourceType):
            raise ValueError(f'Property "SourceType" of "SetDeviceDbSourceRequest" is not an instance of "DeviceDbSourceType".')

        if self.url_or_file_path is not None:
            if not isinstance(self.url_or_file_path, str):
                raise ValueError(f'Property "UrlOrFilePath" of "SetDeviceDbSourceRequest" is not a string.')
