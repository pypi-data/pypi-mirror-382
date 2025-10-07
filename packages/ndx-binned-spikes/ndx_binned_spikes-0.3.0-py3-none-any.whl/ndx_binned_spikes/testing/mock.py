from typing import Optional

from ndx_binned_spikes import BinnedAlignedSpikes, BinnedSpikes
import numpy as np
from hdmf.common import DynamicTableRegion


def mock_BinnedAlignedSpikes(
    number_of_units: int = 2,
    number_of_events: int = 10,
    number_of_bins: int = 3,
    number_of_conditions: int = 5,
    bin_width_in_ms: float = 20.0,
    event_to_bin_offset_in_ms: float = 1.0,
    seed: int = 0,
    event_timestamps: Optional[np.ndarray] = None,
    data: Optional[np.ndarray] = None,
    condition_indices: Optional[np.ndarray] = None,
    condition_labels: Optional[np.ndarray] = None,
    units_region: Optional[DynamicTableRegion] = None,
    sort_data: bool = True,
    add_random_nans: bool = False,
) -> BinnedAlignedSpikes:
    """
    Generate a mock BinnedAlignedSpikes object with specified parameters or from given data.

    Parameters
    ----------
    number_of_units : int, optional
        The number of different units (channels, neurons, etc.) to simulate.
    number_of_events : int, optional
        The number of timestamps of the event that the data is aligned to.
    number_of_bins : int, optional
        The number of bins.
    number_of_conditions : int, optional
        The number of different conditions that the data is aligned to. It should be less than `number_of_events`.
    bin_width_in_ms : float, optional
        The width of each bin in milliseconds.
    event_to_bin_offset_in_ms : float, optional
        The time in milliseconds from the event start to the first bin.
    seed : int, optional
        Seed for the random number generator to ensure reproducibility.
    data : np.ndarray, optional
        A 3D array of shape (number_of_units, number_of_events, number_of_bins) representing
        the binned spike data. If provided, it overrides the generation of mock data based on other parameters.
        Its shape should match the expected number of units, event repetitions, and bins.
    event_timestamps : np.ndarray, optional
        An array of event_timestamps for each event. If not provided, it will be automatically generated.
        It should have size `number_of_events`.
    condition_indices : np.ndarray, optional
        An array of indices characterizing each condition. If not provided, it will be automatically generated
        from the number of conditions and number of events. It should have size `number_of_events`.
        If provided, the `number_of_conditions` parameter will be ignored and the number of conditions will be
        inferred from the unique values in `condition_indices`.
    condition_labels: np.ndarray, optional
        An array of labels for each condition. It should have size `number_of_conditions`.
    units_region: DynamicTableRegion, optional
        A reference to the Units table region that contains the units of the data.
    sort_data: bool, optional
        If True, the data will be sorted by timestamps.
    Returns
    -------
    BinnedAlignedSpikes
        A mock BinnedAlignedSpikes object populated with the provided or generated data and parameters.
    """
    
    if data is not None:
        number_of_units, number_of_events, number_of_bins = data.shape
    else:
        rng = np.random.default_rng(seed=seed)
        data = rng.integers(low=0, high=100, size=(number_of_units, number_of_events, number_of_bins), dtype="uint64")

    # Assert data shapes
    assertion_msg = (
        "The shape of `data` should be `(number_of_units, number_of_events, number_of_bins)`, "
        f"The actual shape is {data.shape} \n "
        f"but {number_of_bins=}, {number_of_events=}, {number_of_units=} was passed"
    )
    assert data.shape == (number_of_units, number_of_events, number_of_bins), assertion_msg

    if event_timestamps is None:
        event_timestamps = np.arange(number_of_events, dtype="float64")

    if event_timestamps.shape[0] != number_of_events:
        raise ValueError("The shape of `event_timestamps` does not match `number_of_events`.")

    if condition_indices is None and number_of_conditions > 0:

        assert (
            number_of_conditions < number_of_events
        ), "The number of conditions should be less than the number of events."

        condition_indices = np.zeros(number_of_events, dtype="uint64")
        all_indices = np.arange(number_of_conditions, dtype='uint64')

        # Ensure all conditions indices appear at least once
        condition_indices[:number_of_conditions] = rng.choice(all_indices, size=number_of_conditions, replace=False)
        # Then fill the rest with random samples
        condition_indices[number_of_conditions:] = rng.choice(
            condition_indices[:number_of_events],
            size=number_of_events - number_of_conditions,
            replace=True,
        )
        

    if condition_indices is not None:
        number_of_conditions = np.unique(condition_indices).size
        
        if condition_labels is not None:
            condition_labels = np.asarray(condition_labels, dtype="U")
            
            if condition_labels.size != number_of_conditions:
                raise ValueError("The number of condition labels should match the number of conditions.")

    # Sort the data by timestamps
    if sort_data:
        sorted_indices = np.argsort(event_timestamps)
        data = data[:, sorted_indices, :]
        if condition_indices is not None:
            condition_indices = condition_indices[sorted_indices]

    # Add random nans over all the data
    if add_random_nans:
        data = data.astype("float32")
        nan_mask = rng.choice([True, False], size=data.shape, p=[0.1, 0.9])
        data[nan_mask] = np.nan

    binned_aligned_spikes = BinnedAlignedSpikes(
        bin_width_in_ms=bin_width_in_ms,
        event_to_bin_offset_in_ms=event_to_bin_offset_in_ms,
        data=data,
        event_timestamps=event_timestamps,
        condition_indices=condition_indices,
        condition_labels=condition_labels,
        units_region=units_region,
    )
    return binned_aligned_spikes


def mock_BinnedSpikes(
    number_of_units: int = 2,
    number_of_bins: int = 10,
    bin_width_in_ms: float = 20.0,
    start_time_in_ms: float = 0.0,
    seed: int = 0,
    data: Optional[np.ndarray] = None,
    units_region: Optional[DynamicTableRegion] = None,
    add_random_nans: bool = False,
) -> BinnedSpikes:
    """
    Generate a mock BinnedSpikes object with specified parameters or from given data.

    Parameters
    ----------
    number_of_units : int, optional
        The number of different units (channels, neurons, etc.) to simulate.
    number_of_bins : int, optional
        The number of bins.
    bin_width_in_ms : float, optional
        The width of each bin in milliseconds.
    start_time_in_ms : float, optional
        The timestamp of the beginning of the first bin in milliseconds.
    seed : int, optional
        Seed for the random number generator to ensure reproducibility.
    data : np.ndarray, optional
        A 2D array of shape (number_of_units, number_of_bins) representing
        the binned spike data. If provided, it overrides the generation of mock data based on other parameters.
    units_region: DynamicTableRegion, optional
        A reference to the Units table region that contains the units of the data.
    add_random_nans: bool, optional
        If True, random NaN values will be added to the data.

    Returns
    -------
    BinnedSpikes
        A mock BinnedSpikes object populated with the provided or generated data and parameters.
    """
    
    if data is not None:
        number_of_units, number_of_bins = data.shape
    else:
        rng = np.random.default_rng(seed=seed)
        data = rng.integers(low=0, high=100, size=(number_of_units, number_of_bins), dtype="uint64")

    # Assert data shapes
    assertion_msg = (
        "The shape of `data` should be `(number_of_units, number_of_bins)`, "
        f"The actual shape is {data.shape} \n "
        f"but {number_of_bins=}, {number_of_units=} was passed"
    )
    assert data.shape == (number_of_units, number_of_bins), assertion_msg

    # Add random nans over all the data
    if add_random_nans:
        data = data.astype("float32")
        rng = np.random.default_rng(seed=seed)
        nan_mask = rng.choice([True, False], size=data.shape, p=[0.1, 0.9])
        data[nan_mask] = np.nan

    binned_spikes = BinnedSpikes(
        bin_width_in_ms=bin_width_in_ms,
        start_time_in_ms=start_time_in_ms,
        data=data,
        units_region=units_region,
    )
    return binned_spikes
