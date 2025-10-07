import os
import numpy as np
from typing import Tuple
from pynwb import load_namespaces, get_class
from pynwb import register_class
from pynwb.core import NWBDataInterface
from hdmf.utils import docval
from hdmf.common import DynamicTableRegion

from importlib.resources import files


# Get path to the namespace.yaml file with the expected location when installed not in editable mode
__location_of_this_file = files(__name__)
__spec_path = __location_of_this_file / "spec" / "ndx-binned-spikes.namespace.yaml"

# If that path does not exist, we are likely running in editable mode. Use the local path instead
if not os.path.exists(__spec_path):
    __spec_path = __location_of_this_file.parent.parent.parent / "spec" / "ndx-binned-spikes.namespace.yaml"

# Load the namespace
load_namespaces(str(__spec_path))

# BinnedAlignedSpikes = get_class("BinnedAlignedSpikes", "ndx-binned-spikes")


@register_class(neurodata_type="BinnedAlignedSpikes", namespace="ndx-binned-spikes")  # noqa
class BinnedAlignedSpikes(NWBDataInterface):
    __nwbfields__ = (
        "name",
        "description",
        "bin_width_in_ms",
        "event_to_bin_offset_in_ms",
        "data",
        "timestamps",
        "condition_indices",
        "condition_labels",
        {"name": "units_region", "child": True},  # TODO, I forgot why this is included
    )

    DEFAULT_NAME = "BinnedAlignedSpikes"
    DEFAULT_DESCRIPTION = "Spikes data binned and aligned to the event timestamps of one or multiple conditions."

    @docval(
        {
            "name": "name",
            "type": str,
            "doc": "The name of this container",
            "default": DEFAULT_NAME,
        },
        {
            "name": "description",
            "type": str,
            "doc": "A description of what the data represents",
            "default": DEFAULT_DESCRIPTION,
        },
        {
            "name": "bin_width_in_ms",
            "type": float,
            "doc": "The length in milliseconds of the bins",
        },
        {
            "name": "event_to_bin_offset_in_ms",
            "type": float,
            "doc": (
                "The time in milliseconds from the event to the beginning of the first bin. A negative value indicates"
                "that the first bin is before the event whereas a positive value indicates that the first bin is "
                "after the event."
            ),
            "default": 0.0,
        },
        {
            "name": "data",
            "type": "array_data",
            "shape": [(None, None, None)],
            "doc": (
                "The binned data. It should be an array whose first dimension is the number of units, "
                "the second dimension is the number of events, and the third dimension is the number of bins."
            ),
        },
        {
            "name": "event_timestamps",
            "type": "array_data",
            "doc": (
                "The timestamps at which the events occurred. It is assumed that they map positionally to "
                "the second index of the data.",
            ),
            "shape": (None,),
        },
        {
            "name": "condition_indices",
            "type": "array_data",
            "doc": (
                "The index of the condition that each entry of `event_timestamps` corresponds to "
                "(e.g. a stimuli type, trial number, category, etc.)."
                "This is only used when the data is aligned to multiple conditions"
            ),
            "shape": (None,),
            "default": None,
        },
        {
            "name":"condition_labels",
            "type": "array_data",
            "doc": (
                "The labels of the conditions that the data is aligned to. The size of this array should match "
                "the number of conditions. This is only used when the data is aligned to multiple conditions. "
                "First condition is index 0, second is index 1, etc."
            ),
            "shape": (None,),
            "default": None,
        },
        {
            "name": "units_region",
            "type": DynamicTableRegion,
            "doc": "A reference to the Units table region that contains the units of the data.",
            "default": None,
        },
    )
    def __init__(self, **kwargs):

        name = kwargs.pop("name")
        super().__init__(name=name)

        event_timestamps = kwargs["event_timestamps"]
        data = kwargs["data"]

        if data.shape[1] != event_timestamps.shape[0]:
            msg = (
                f"The number of event_timestamps must match the second axis of data: \n"
                f"event_timestamps.size: {event_timestamps.size} \n" 
                f"data.shape[1]: {data.shape[1]}"
            )
            raise ValueError(msg)

        # Assert timestamps are monotonically increasing
        if not np.all(np.diff(kwargs["event_timestamps"]) >= 0):
            error_msg = (
                "The event_timestamps must be monotonically increasing and the data and condition_indices "
                "must be sorted by event_timestamps. Use the `BinnedAlignedSpikes.sort_data_by_timestamps` "
                "method to do this automatically before initializing `BinnedAlignedSpikes`."
            )
            raise ValueError(error_msg)

        # Condition indices check
        condition_indices = kwargs.get("condition_indices", None)
        self.has_multiple_conditions = condition_indices is not None
        if self.has_multiple_conditions:
            assert (
                condition_indices.shape[0] == event_timestamps.shape[0]
            ), "The number of event_timestamps must match the condition_indices."

        for key in kwargs:
            setattr(self, key, kwargs[key])

    def get_data_for_condition(self, condition_index):

        if not self.has_multiple_conditions:
            return self.data

        mask = self.condition_indices[:] == condition_index
        binned_spikes_for_unit = self.data[:, mask, :]

        return binned_spikes_for_unit

    def get_event_timestamps_for_condition(self, condition_index):

        if not self.has_multiple_conditions:
            return self.event_timestamps

        mask = self.condition_indices == condition_index
        event_timestamps = self.event_timestamps[mask]

        return event_timestamps

    @staticmethod
    def sort_data_by_event_timestamps(
        data: np.ndarray,
        event_timestamps: np.ndarray,
        condition_indices: np.ndarray,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:

        sorted_indices = np.argsort(event_timestamps)
        data = data[:, sorted_indices, :]
        event_timestamps = event_timestamps[sorted_indices]
        condition_indices = condition_indices[sorted_indices]

        return data, event_timestamps, condition_indices

    @property
    def number_of_units(self):
        return self.data.shape[0]

    @property
    def number_of_events(self):
        return self.data.shape[1]

    @property
    def number_of_bins(self):
        return self.data.shape[2]
    

    @property
    def number_of_conditions(self):
        if self.has_multiple_conditions:
            return np.unique(self.condition_indices).size
        else:
            return 1

@register_class(neurodata_type="BinnedSpikes", namespace="ndx-binned-spikes")  # noqa
class BinnedSpikes(NWBDataInterface):
    __nwbfields__ = (
        "name",
        "description",
        "bin_width_in_ms",
        "start_time_in_ms",
        "data",
        {"name": "units_region", "child": True},
    )

    DEFAULT_NAME = "BinnedSpikes"
    DEFAULT_DESCRIPTION = "Binned spike counts."

    @docval(
        {
            "name": "name",
            "type": str,
            "doc": "The name of this container",
            "default": DEFAULT_NAME,
        },
        {
            "name": "description",
            "type": str,
            "doc": "A description of what the data represents",
            "default": DEFAULT_DESCRIPTION,
        },
        {
            "name": "bin_width_in_ms",
            "type": float,
            "doc": "The length in milliseconds of the bins",
        },
        {
            "name": "start_time_in_ms",
            "type": float,
            "doc": (
                "The timestamp of the beginning of the first bin in milliseconds. The default "
                "value is 0, which represents the beginning of the session."
            ),
            "default": 0.0,
        },
        {
            "name": "data",
            "type": "array_data",
            "shape": [(None, None)],
            "doc": (
                "The binned data. It should be an array whose first dimension is the number of units, "
                "and the second dimension is the number of bins."
            ),
        },
        {
            "name": "units_region",
            "type": DynamicTableRegion,
            "doc": "A reference to the Units table region that contains the units of the data.",
            "default": None,
        },
    )
    def __init__(self, **kwargs):
        name = kwargs.pop("name")
        super().__init__(name=name)

        for key in kwargs:
            setattr(self, key, kwargs[key])

    @property
    def number_of_units(self):
        return self.data.shape[0]

    @property
    def number_of_bins(self):
        return self.data.shape[1]


# Remove these functions from the package
del load_namespaces, get_class
