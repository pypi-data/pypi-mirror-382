"""Unit and integration tests for the example BinnedAlignedSpikes extension neurodata type."""

import numpy as np

from pynwb import NWBHDF5IO
from pynwb.testing.mock.file import mock_NWBFile
from pynwb.testing import TestCase, remove_test_file
from hdmf.common import DynamicTableRegion
from pynwb.misc import Units
from ndx_binned_spikes import BinnedAlignedSpikes
from ndx_binned_spikes.testing.mock import mock_BinnedAlignedSpikes
from pynwb.testing.mock.ecephys import mock_Units


class TestBinnedAlignedSpikesConstructor(TestCase):
    """Simple unit test for creating a BinnedAlignedSpikes."""

    def setUp(self):
        """Set up an NWB file. Necessary because BinnedAlignedSpikes requires references to electrodes."""

        self.number_of_units = 2
        self.number_of_bins = 3
        self.number_of_events = 4
        self.bin_width_in_ms = 20.0
        self.event_to_bin_offset_in_ms = -100.0
        self.rng = np.random.default_rng(seed=0)

        self.data = self.rng.integers(
            low=0,
            high=100,
            size=(
                self.number_of_units,
                self.number_of_events,
                self.number_of_bins,
            ),
        )

        self.event_timestamps = np.arange(self.number_of_events, dtype="float64")

        self.nwbfile = mock_NWBFile()

    def test_constructor(self):
        """Test that the constructor for BinnedAlignedSpikes sets values as expected."""

        binned_aligned_spikes = BinnedAlignedSpikes(
            bin_width_in_ms=self.bin_width_in_ms,
            event_to_bin_offset_in_ms=self.event_to_bin_offset_in_ms,
            data=self.data,
            event_timestamps=self.event_timestamps,
        )

        np.testing.assert_array_equal(binned_aligned_spikes.data, self.data)
        np.testing.assert_array_equal(binned_aligned_spikes.event_timestamps, self.event_timestamps)

        self.assertEqual(binned_aligned_spikes.bin_width_in_ms, self.bin_width_in_ms)
        self.assertEqual(
            binned_aligned_spikes.event_to_bin_offset_in_ms, self.event_to_bin_offset_in_ms
        )

        self.assertEqual(binned_aligned_spikes.number_of_units, self.number_of_units)
        self.assertEqual(binned_aligned_spikes.number_of_events, self.number_of_events)
        self.assertEqual(binned_aligned_spikes.number_of_bins, self.number_of_bins)

    def test_constructor_units_region(self):

        units_table = Units()
        units_table.add_column(name="unit_name", description="a readable identifier for the units")

        unit_name_a = "a"
        spike_times_a = [1.1, 2.2, 3.3]
        units_table.add_row(spike_times=spike_times_a, unit_name=unit_name_a)

        unit_name_b = "b"
        spike_times_b = [4.4, 5.5, 6.6]
        units_table.add_row(spike_times=spike_times_b, unit_name=unit_name_b)

        unit_name_c = "c"
        spike_times_c = [7.7, 8.8, 9.9]
        units_table.add_row(spike_times=spike_times_c, unit_name=unit_name_c)

        region_indices = [0, 2]
        units_region = DynamicTableRegion(
            data=region_indices, table=units_table, description="region of units table", name="units_region"
        )

        binned_aligned_spikes = BinnedAlignedSpikes(
            bin_width_in_ms=self.bin_width_in_ms,
            event_to_bin_offset_in_ms=self.event_to_bin_offset_in_ms,
            data=self.data,
            event_timestamps=self.event_timestamps,
            units_region=units_region,
        )

        unit_table_indices = binned_aligned_spikes.units_region.data
        unit_table_names = binned_aligned_spikes.units_region.table["unit_name"][unit_table_indices]

        expected_names = [unit_name_a, unit_name_c]
        self.assertListEqual(unit_table_names, expected_names)

    def test_constructor_inconsistent_timestamps_and_data_error(self):
        shorter_timestamps = self.event_timestamps[:-1]

        with self.assertRaises(ValueError):
            BinnedAlignedSpikes(
                bin_width_in_ms=self.bin_width_in_ms,
                event_to_bin_offset_in_ms=self.event_to_bin_offset_in_ms,
                data=self.data,
                event_timestamps=shorter_timestamps,
            )


class TestBinnedAlignedSpikesMultipleConditions(TestCase):
    """Simple unit test for creating a BinnedAlignedSpikes with multiple conditions."""

    def setUp(self):
        """Set up an NWB file.."""

        self.number_of_units = 2
        self.number_of_bins = 4
        self.number_of_events = 5
        self.number_of_conditions = 2

        self.bin_width_in_ms = 20.0
        self.event_to_bin_offset_in_ms = -100.0

        # Two units in total and 4 bins, and condition with two timestamps
        self.data_for_first_condition = np.array(
            [
                # Unit 1 data
                [
                    [0, 1, 2, 3],  # Bin counts around the first timestamp
                    [4, 5, 6, 7],  # Bin counts around the second timestamp
                ],
                # Unit 2 data
                [
                    [8, 9, 10, 11],  # Bin counts around the first timestamp
                    [12, 13, 14, 15],  # Bin counts around the second timestamp
                ],
            ],
            dtype="uint64",

        )

        # Also two units and 4 bins but this condition appeared three times
        self.data_for_second_condition = np.array(
            [
                # Unit 1 data
                [
                    [0, 1, 2, 3],  # Bin counts around the first timestamp
                    [4, 5, 6, 7],  # Bin counts around the second timestamp
                    [8, 9, 10, 11],  # Bin counts around the third timestamp
                ],
                # Unit 2 data
                [
                    [12, 13, 14, 15],  # Bin counts around the first timestamp
                    [16, 17, 18, 19],  # Bin counts around the second timestamp
                    [20, 21, 22, 23],  # Bin counts around the third timestamp
                ],
            ],
            dtype="uint64",
        )

        self.timestamps_first_condition = [5.0, 15.0]
        self.timestamps_second_condition = [0.0, 10.0, 20.0]

        data_list = [self.data_for_first_condition, self.data_for_second_condition]
        self.data = np.concatenate(data_list, axis=1)

        indices_list = [np.full(data.shape[1], condition_index) for condition_index, data in enumerate(data_list)]
        self.condition_indices = np.concatenate(indices_list)

        self.event_timestamps = np.concatenate([self.timestamps_first_condition, self.timestamps_second_condition])

        self.sorted_indices = np.argsort(self.event_timestamps)

        self.condition_labels = ["first", "second"]

    def test_constructor(self):
        """Test that the constructor for BinnedAlignedSpikes sets values as expected."""

        # Test error if the timestamps are not sorted and/or aligned to conditions
        with self.assertRaises(ValueError):
            BinnedAlignedSpikes(
                bin_width_in_ms=self.bin_width_in_ms,
                event_to_bin_offset_in_ms=self.event_to_bin_offset_in_ms,
                data=self.data,
                event_timestamps=self.event_timestamps,
                condition_indices=self.condition_indices,
            )

        data, event_timestamps, condition_indices = BinnedAlignedSpikes.sort_data_by_event_timestamps(
            self.data,
            self.event_timestamps,
            self.condition_indices,
        )

        binnned_align_spikes = BinnedAlignedSpikes(
            bin_width_in_ms=self.bin_width_in_ms,
            event_to_bin_offset_in_ms=self.event_to_bin_offset_in_ms,
            data=data,
            event_timestamps=event_timestamps,
            condition_indices=condition_indices,
            condition_labels=self.condition_labels,
        )

        np.testing.assert_array_equal(binnned_align_spikes.data, self.data[:, self.sorted_indices, :])
        np.testing.assert_array_equal(
            binnned_align_spikes.condition_indices, self.condition_indices[self.sorted_indices]
        )
        np.testing.assert_array_equal(binnned_align_spikes.event_timestamps, self.event_timestamps[self.sorted_indices])

        np.testing.assert_array_equal(binnned_align_spikes.condition_labels, self.condition_labels)

        self.assertEqual(binnned_align_spikes.bin_width_in_ms, self.bin_width_in_ms)
        self.assertEqual(
            binnned_align_spikes.event_to_bin_offset_in_ms,
            self.event_to_bin_offset_in_ms,
        )

        self.assertEqual(binnned_align_spikes.number_of_units, self.number_of_units)
        self.assertEqual(binnned_align_spikes.number_of_events, self.number_of_events)
        self.assertEqual(binnned_align_spikes.number_of_bins, self.number_of_bins)

    def test_get_single_condition_data_methods(self):

        data, event_timestamps, condition_indices = BinnedAlignedSpikes.sort_data_by_event_timestamps(
            self.data,
            self.event_timestamps,
            self.condition_indices,
        )

        binnned_align_spikes = BinnedAlignedSpikes(
            bin_width_in_ms=self.bin_width_in_ms,
            event_to_bin_offset_in_ms=self.event_to_bin_offset_in_ms,
            data=data,
            event_timestamps=event_timestamps,
            condition_indices=condition_indices,
        )

        data_condition1 = binnned_align_spikes.get_data_for_condition(condition_index=0)
        np.testing.assert_allclose(data_condition1, self.data_for_first_condition)

        data_condition2 = binnned_align_spikes.get_data_for_condition(condition_index=1)
        np.testing.assert_allclose(data_condition2, self.data_for_second_condition)

        timestamps_condition1 = binnned_align_spikes.get_event_timestamps_for_condition(condition_index=0)
        np.testing.assert_allclose(timestamps_condition1, self.timestamps_first_condition)

        timestamps_condition2 = binnned_align_spikes.get_event_timestamps_for_condition(condition_index=1)
        np.testing.assert_allclose(timestamps_condition2, self.timestamps_second_condition)


class TestBinnedAlignedSpikesSimpleRoundtrip(TestCase):
    """Simple roundtrip test for BinnedAlignedSpikes."""

    def setUp(self):
        self.nwbfile = mock_NWBFile()

        self.path = "test.nwb"

    def tearDown(self):
        remove_test_file(self.path)

    def test_roundtrip_acquisition(self):
        """
        Add a BinnedAlignedSpikes to an NWBFile, write it to file, read the file
        and test that the BinnedAlignedSpikes from the file matches the original BinnedAlignedSpikes.
        """
        # Testing here
        number_of_units = 5
        number_of_bins = 10
        number_of_events = 100
        number_of_conditions = 3
        condition_labels = ["a", "b", "c"]

        binned_aligned_spikes = mock_BinnedAlignedSpikes(
            number_of_units=number_of_units,
            number_of_bins=number_of_bins,
            number_of_events=number_of_events,
            number_of_conditions=number_of_conditions,
            condition_labels=condition_labels,
        )

        self.nwbfile.add_acquisition(binned_aligned_spikes)

        with NWBHDF5IO(self.path, mode="w") as io:
            io.write(self.nwbfile)

        with NWBHDF5IO(self.path, mode="r", load_namespaces=True) as io:
            read_nwbfile = io.read()
            read_binned_aligned_spikes = read_nwbfile.acquisition["BinnedAlignedSpikes"]
            self.assertContainerEqual(binned_aligned_spikes, read_binned_aligned_spikes)

            assert read_binned_aligned_spikes.number_of_units == number_of_units
            assert read_binned_aligned_spikes.number_of_bins == number_of_bins
            assert read_binned_aligned_spikes.number_of_events == number_of_events
            assert read_binned_aligned_spikes.number_of_conditions == number_of_conditions
            
            expected_data_condition1 = binned_aligned_spikes.get_data_for_condition(condition_index=2)
            data_condition1 = read_binned_aligned_spikes.get_data_for_condition(condition_index=2)

            np.testing.assert_equal(data_condition1, expected_data_condition1)

    def test_roundtrip_processing_module(self):
        binned_aligned_spikes = mock_BinnedAlignedSpikes()

        ecephys_processinng_module = self.nwbfile.create_processing_module(name="ecephys", description="a description")
        ecephys_processinng_module.add(binned_aligned_spikes)

        with NWBHDF5IO(self.path, mode="w") as io:
            io.write(self.nwbfile)

        with NWBHDF5IO(self.path, mode="r", load_namespaces=True) as io:
            read_nwbfile = io.read()
            read_container = read_nwbfile.processing["ecephys"]["BinnedAlignedSpikes"]
            self.assertContainerEqual(binned_aligned_spikes, read_container)

    def test_roundtrip_with_units_table(self):

        units = mock_Units(num_units=3)
        self.nwbfile.units = units
        region_indices = [0, 3]
        units_region = DynamicTableRegion(
            data=region_indices, table=units, description="region of units table", name="units_region"
        )

        binned_aligned_spikes_with_region = mock_BinnedAlignedSpikes(units_region=units_region)
        self.nwbfile.add_acquisition(binned_aligned_spikes_with_region)

        with NWBHDF5IO(self.path, mode="w") as io:
            io.write(self.nwbfile)

        with NWBHDF5IO(self.path, mode="r", load_namespaces=True) as io:
            read_nwbfile = io.read()
            read_binned_aligned_spikes = read_nwbfile.acquisition["BinnedAlignedSpikes"]
            self.assertContainerEqual(binned_aligned_spikes_with_region, read_binned_aligned_spikes)


    def test_data_with_nans(self):
        
        binned_aligned_spikes = mock_BinnedAlignedSpikes(add_random_nans=True)

        self.nwbfile.add_acquisition(binned_aligned_spikes)

        with NWBHDF5IO(self.path, mode="w") as io:
            io.write(self.nwbfile)

        with NWBHDF5IO(self.path, mode="r", load_namespaces=True) as io:
            read_nwbfile = io.read()
            read_binned_aligned_spikes = read_nwbfile.acquisition["BinnedAlignedSpikes"]
            self.assertContainerEqual(binned_aligned_spikes, read_binned_aligned_spikes)
