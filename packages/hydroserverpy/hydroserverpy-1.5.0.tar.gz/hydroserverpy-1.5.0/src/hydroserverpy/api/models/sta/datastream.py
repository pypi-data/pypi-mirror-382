import uuid
import pandas as pd
from typing import List, Union, Optional, Literal, ClassVar, TYPE_CHECKING
from pydantic import Field
from uuid import UUID
from datetime import datetime
from hydroserverpy.api.utils import normalize_uuid
from ..base import HydroServerBaseModel

if TYPE_CHECKING:
    from hydroserverpy import HydroServer
    from hydroserverpy.api.models import (
        Workspace,
        Thing,
        Sensor,
        ObservedProperty,
        Unit,
        ProcessingLevel,
        DataSource,
        DataArchive
    )


class Datastream(HydroServerBaseModel):
    name: str = Field(..., max_length=255)
    description: str
    observation_type: str = Field(..., max_length=255)
    sampled_medium: str = Field(..., max_length=255)
    no_data_value: float
    aggregation_statistic: str = Field(..., max_length=255)
    time_aggregation_interval: float
    status: Optional[str] = Field(None, max_length=255)
    result_type: str = Field(..., max_length=255)
    value_count: Optional[int] = Field(None, ge=0)
    phenomenon_begin_time: Optional[datetime] = None
    phenomenon_end_time: Optional[datetime] = None
    result_begin_time: Optional[datetime] = None
    result_end_time: Optional[datetime] = None
    is_private: bool = False
    is_visible: bool = True
    time_aggregation_interval_unit: Literal["seconds", "minutes", "hours", "days"]
    intended_time_spacing: Optional[float] = None
    intended_time_spacing_unit: Optional[
        Literal["seconds", "minutes", "hours", "days"]
    ] = None
    data_source_id: Optional[uuid.UUID] = None
    thing_id: uuid.UUID
    workspace_id: uuid.UUID
    sensor_id: uuid.UUID
    observed_property_id: uuid.UUID
    processing_level_id: uuid.UUID
    unit_id: uuid.UUID

    _editable_fields: ClassVar[set[str]] = {
        "name", "description", "observation_type", "sampled_medium", "no_data_value", "aggregation_statistic",
        "time_aggregation_interval", "status", "result_type", "value_count", "phenomenon_begin_time",
        "phenomenon_end_time", "result_begin_time", "result_end_time", "is_private", "is_visible",
        "time_aggregation_interval_unit", "intended_time_spacing", "intended_time_spacing_unit", "thing_id",
        "sensor_id", "observed_property_id", "processing_level_id", "unit_id"
    }

    def __init__(self, client: "HydroServer", **data):
        super().__init__(client=client, service=client.datastreams, **data)

        self._workspace = None
        self._thing = None
        self._observed_property = None
        self._unit = None
        self._processing_level = None
        self._sensor = None
        self._data_source = None
        self._data_archives = None

    @classmethod
    def get_route(cls):
        return "datastreams"

    @property
    def workspace(self) -> "Workspace":
        """The workspace this datastream belongs to."""

        if self._workspace is None:
            self._workspace = self.client.workspaces.get(uid=self.workspace_id)

        return self._workspace

    @property
    def thing(self) -> "Thing":
        """The thing this datastream belongs to."""

        if self._thing is None:
            self._thing = self.client.things.get(uid=self.thing_id)

        return self._thing

    @thing.setter
    def thing(self, thing: Union["Thing", UUID, str] = ...):
        if not thing:
            raise ValueError("Thing of datastream cannot be None.")
        if normalize_uuid(thing) != str(self.thing_id):
            self.thing_id = normalize_uuid(thing)
            self._thing = None

    @property
    def sensor(self) -> "Sensor":
        """The sensor of this datastream."""

        if self._sensor is None:
            self._sensor = self.client.sensors.get(uid=self.sensor_id)

        return self._sensor

    @sensor.setter
    def sensor(self, sensor: Union["Sensor", UUID, str] = ...):
        if not sensor:
            raise ValueError("Sensor of datastream cannot be None.")
        if normalize_uuid(sensor) != str(self.sensor_id):
            self.sensor_id = normalize_uuid(sensor)
            self._sensor = None

    @property
    def observed_property(self) -> "ObservedProperty":
        """The observed property of this datastream."""

        if self._observed_property is None:
            self._observed_property = self.client.observedproperties.get(uid=self.observed_property_id)

        return self._observed_property

    @observed_property.setter
    def observed_property(self, observed_property: Union["ObservedProperty", UUID, str] = ...):
        if not observed_property:
            raise ValueError("Observed property of datastream cannot be None.")
        if normalize_uuid(observed_property) != str(self.observed_property_id):
            self.observed_property_id = normalize_uuid(observed_property)
            self._observed_property = None

    @property
    def unit(self) -> "Unit":
        """The unit of this datastream."""

        if self._unit is None:
            self._unit = self.client.units.get(uid=self.unit_id)

        return self._unit

    @unit.setter
    def unit(self, unit: Union["Unit", UUID, str] = ...):
        if not unit:
            raise ValueError("Unit of datastream cannot be None.")
        if normalize_uuid(unit) != str(self.unit_id):
            self.unit_id = normalize_uuid(unit)
            self._unit = None

    @property
    def processing_level(self) -> "ProcessingLevel":
        """The processing level of this datastream."""

        if self._processing_level is None:
            self._processing_level = self.client.processinglevels.get(uid=self.processing_level_id)

        return self._processing_level

    @processing_level.setter
    def processing_level(self, processing_level: Union["ProcessingLevel", UUID, str] = ...):
        if not processing_level:
            raise ValueError("Processing level of datastream cannot be None.")
        if normalize_uuid(processing_level) != str(self.processing_level_id):
            self.processing_level_id = normalize_uuid(processing_level)
            self._processing_level = None

    @property
    def data_source(self) -> Optional["DataSource"]:
        """The data source of this datastream."""

        if self._data_source is None and self.data_source_id is not None:
            self._data_source = self.client.datasources.get(uid=self.data_source_id)

        return self._data_source

    @property
    def data_archives(self) -> List["DataArchive"]:
        """The data archives of this datastream."""

        if self._data_archives is None:
            self._data_archives = self.client.dataarchives.list(datastream=self.uid, fetch_all=True).items

        return self._data_archives

    def get_observations(
        self,
        page: int = ...,
        page_size: int = 100000,
        order_by: List[str] = ...,
        phenomenon_time_max: datetime = ...,
        phenomenon_time_min: datetime = ...,
        result_qualifier_code: str = ...,
        fetch_all: bool = False,
    ) -> pd.DataFrame:
        """Retrieve the observations for this datastream."""

        return self.client.datastreams.get_observations(
            uid=self.uid,
            page=page,
            page_size=page_size,
            order_by=order_by,
            phenomenon_time_max=phenomenon_time_max,
            phenomenon_time_min=phenomenon_time_min,
            result_qualifier_code=result_qualifier_code,
            fetch_all=fetch_all
        )

    def load_observations(
        self,
        observations: pd.DataFrame,
        mode: str = "insert"
    ) -> None:
        """Load a DataFrame of observations to the datastream."""

        return self.client.datastreams.load_observations(
            uid=self.uid,
            observations=observations,
            mode=mode
        )

    def delete_observations(
        self,
        phenomenon_time_start: Optional[datetime] = None,
        phenomenon_time_end: Optional[datetime] = None,
    ):
        """Delete the observations for this datastream."""

        return self.client.datastreams.delete_observations(
            uid=self.uid,
            phenomenon_time_start=phenomenon_time_start,
            phenomenon_time_end=phenomenon_time_end,
        )

    # TODO: Find a better long-term solution for this issue.
    def sync_phenomenon_end_time(self):
        """Ensures the phenomenon_end_time field matches the actual end time of the observations."""

        path = f"/{self.client.base_route}/{self.get_route()}/{str(self.uid)}/observations"
        response = self.client.request(
            "get", path, params={"page_size": 1, "order_by": "-phenomenonTime"}

        ).json()

        if len(response) > 0:
            self.phenomenon_end_time = datetime.fromisoformat(response[0]["phenomenonTime"])
        else:
            self.phenomenon_end_time = None

        self.save()
