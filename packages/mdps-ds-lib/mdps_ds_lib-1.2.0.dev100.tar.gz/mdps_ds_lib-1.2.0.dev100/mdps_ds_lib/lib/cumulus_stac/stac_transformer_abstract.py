import logging
from abc import ABC, abstractmethod

from mdps_ds_lib.lib.utils.time_utils import TimeUtils

LOGGER = logging.getLogger(__name__)


class StacTransformerAbstract(ABC):
    def __init__(self) -> None:
        super().__init__()
        self._dt_formats = [
            '%y-%m-%dT%H:%M:%S.%f%z',
            '%y-%m-%dT%H:%M:%S%z',
            '%Y-%m-%dT%H:%M:%S.%f%z',
            '%Y-%m-%dT%H:%M:%S%z',
            '%Y-%m-%dT%H:%M:%S.%f',
        ]

    def get_time_obj(self, datetime_str: str):
        if datetime_str is None:
            return None
        for each_fmt in self._dt_formats:
            try:
                dt_utils = TimeUtils().parse_from_str(datetime_str, each_fmt)
                return dt_utils.get_datetime_obj()
            except ValueError as ve1:
                LOGGER.debug(f'format and value do not match: {each_fmt} v. {datetime_str}')
        raise ValueError(f'unknown format: {datetime_str}')

    @abstractmethod
    def to_stac(self, source: dict) -> dict:
        return {}

    @abstractmethod
    def from_stac(self, source: dict) -> dict:
        return {}
