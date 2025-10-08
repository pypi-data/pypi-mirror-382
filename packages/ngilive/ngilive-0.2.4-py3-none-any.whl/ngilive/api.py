from datetime import datetime
import logging
from typing import Any, ParamSpec
from uuid import UUID

import httpx
from pydantic import AwareDatetime, BaseModel

from ngilive.auth import Auth, AuthorizationCode
from ngilive.config import BASE_URL
from ngilive.httpx_wrapper import HTTPXWrapper
from ngilive.log import default_handler


class EventResponse(BaseModel):
    event_id: UUID
    time_from: AwareDatetime
    time_to: AwareDatetime | None = None
    type: str
    tags: list[str]


class CoordinateSystem(BaseModel):
    authority: str
    srid: str | int | None = None


class SensorLocation(BaseModel):
    north: float | None = None
    east: float | None = None
    mash: float | None = None
    coordinateSystem: CoordinateSystem | None = None


class SensorMeta(BaseModel):
    name: str | None = None
    unit: str | None = None
    logger: str | None = None
    type: str
    pos: SensorLocation


class SensorMetaResponse(BaseModel):
    sensors: list[SensorMeta]


class SensorName(BaseModel):
    name: str


class Datapoint(BaseModel):
    timestamp: AwareDatetime
    value: float


class JsonData(BaseModel):
    sensor: SensorName
    data: list[Datapoint]


class JsonDataResponse(BaseModel):
    # {
    #   "data": [
    #     {
    #       "sensor": {
    #         "name": "string"
    #       },
    #       "data": [
    #         {
    #           "timestamp": "2025-10-04T15:26:34.172Z",
    #           "value": 0
    #         }
    #       ]
    #     }
    #   ]
    # }

    data: list[JsonData]


P = ParamSpec("P")


class API:
    def __init__(
        self,
        base_url: str = BASE_URL,
        loglevel: str = "INFO",
        auth: Auth | None = None,
    ) -> None:
        self._logger = logging.getLogger("ngilive.api")
        self._logger.setLevel(loglevel)
        if not self._logger.handlers:
            self._logger.addHandler(default_handler())

        self._c = httpx.Client()
        self._base = base_url
        self._logger.debug(f"Initialized api with base url {base_url}")

        if auth is not None:
            self._logger.debug(f"Using user specified auth provider {type(auth)}")
            self._auth = auth
        else:
            self._auth = AuthorizationCode(loglevel=loglevel)
            self._logger.debug(f"Using default Auth provider {type(self._auth)}")

        self._httpx = HTTPXWrapper(loglevel)

    @property
    def base_url(self):
        return self._base

    def get_token(self) -> str:
        return self._auth.get_token()

    def query_sensors(
        self,
        project: int,
        name: str | list[str] | None = None,
        type: str | list[str] | None = None,
        unit: str | list[str] | None = None,
        logger: str | list[str] | None = None,
    ) -> SensorMetaResponse:
        """Retrieve sensors within a project.

        This endpoint returns the sensors configured for a given project.
        The response can be filtered by sensor name, type, unit, or logger.
        Note that the same sensor may exist in multiple loggers.

        Args:
            project (int):
                Project number.
            name (str | list[str] | None, optional):
                Filters response by sensor name. Note that the same sensor might exist in multiple loggers.
            type (str | list[str] | None, optional):
                Filter by sensor type (e.g., ``"Infiltrasjonstrykk"``).
            unit (str | list[str] | None, optional):
                Filter by configured sensor unit (e.g., ``"mm"``, ``"kPa"``).
            logger (str | list[str] | None, optional):
                Filters the response by logger name.
        """

        params = {}
        if name is not None:
            params["name"] = name

        if type is not None:
            params["type"] = type

        if unit is not None:
            params["unit"] = unit

        if logger is not None:
            params["logger"] = logger

        res = self._httpx.get(
            f"{self._base}/projects/{project}/sensors",
            params=params,
            headers={"Authorization": f"Bearer {self.get_token()}"},
        )
        res.raise_for_status()

        return SensorMetaResponse.model_validate(res.json())

    def query_datapoints(
        self,
        project_number: int,
        start: datetime,
        end: datetime,
        offset: int | None = None,
        limit: int | None = None,
        name: str | list[str] | None = None,
        type: str | list[str] | None = None,
        unit: str | list[str] | None = None,
        logger: str | list[str] | None = None,
    ) -> JsonDataResponse:
        """Retrieve datapoints within a project.

        This endpoint returns datapoints for a given project in the specified
        time interval. Results can be paginated using ``offset`` and ``limit``,
        and filtered by sensor attributes such as name, type, unit, or logger.

        Args:
            project_number (int):
                Project number.
            start (datetime):
                Start time of datapoints time series.
            end (datetime):
                End time of datapoints time series.
            offset (int | None, optional):
                The amount of points that will be skipped before returning data
                in the query. Used in conjunction with ``limit`` when paging
                through the data. Example: ``offset=5000&limit=2000`` will return
                points 5000–7000.
            limit (int | None, optional):
                The amount of points that will be returned in the query. Used in
                conjunction with ``offset`` when paging through the data. Example:
                ``offset=5000&limit=2000`` will return points 5000–7000.
            name (str | list[str] | None, optional):
                Filters response by sensor name. Note that the same sensor might
                exist in multiple loggers.
            type (str | list[str] | None, optional):
                Filters the response by sensor type, for example ``"Infiltrasjonstrykk"``.
            unit (str | list[str] | None, optional):
                Filters the response by configured sensor unit, for example
                ``"mm"`` or ``"kPa"``.
            logger (str | list[str] | None, optional):
                Filters the response by logger name.
        """

        params: dict[str, Any] = {"start": start.isoformat(), "end": end.isoformat()}

        if offset is not None:
            params["offset"] = offset

        if limit is not None:
            params["limit"] = limit

        if name is not None:
            params["name"] = name

        if type is not None:
            params["type"] = type

        if unit is not None:
            params["unit"] = unit

        if logger is not None:
            params["logger"] = logger

        res = self._httpx.get(
            f"{self._base}/projects/{project_number}/datapoints/json_array_v0",
            params=params,
            headers={"Authorization": f"Bearer {self.get_token()}"},
        )
        res.raise_for_status()

        return JsonDataResponse.model_validate(res.json())

    def get_event(self, event_id: UUID) -> EventResponse:
        res = self._httpx.get(
            f"{self._base}/event/{event_id}",
            headers={"Authorization": f"Bearer {self.get_token()}"},
        )
        res.raise_for_status()

        return EventResponse.model_validate(res.json())
