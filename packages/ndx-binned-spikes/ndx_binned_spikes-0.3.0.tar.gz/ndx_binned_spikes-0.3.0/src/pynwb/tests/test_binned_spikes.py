"""Unit and integration tests for the BinnedSpikes extension neurodata type."""

import numpy as np

from pynwb import NWBHDF5IO
from pynwb.testing.mock.file import mock_NWBFile
from pynwb.testing import TestCase, remove_test_file
from hdmf.common import DynamicTableRegion
from pynwb.misc import Units
from ndx_binned_spikes import BinnedSpikes
from ndx_binned_spikes.testing.mock import mock_BinnedSpikes
from pynwb.testing.mock.ecephys import mock_Units


class TestBinnedSpikesConstructor(TestCase):
    """Simple unit test for creating a BinnedSpikes."""

    def setUp(self):
        """Set up an NWB file. Necessary because BinnedSpikes may reference units."""

        self.number_of_units = 2
        self.number_of_bins = 10
        self.bin_width_in_ms = 20.0
        self.start_time_in_ms = -100.0
        self.rng = np.random.default_rng(seed=0)

        self.data = self.rng.integers(
            low=0,
            high=100,
            size=(
                self.number_of_units,
                self.number_of_bins,
            ),
        )

        self.nwbfile = mock_NWBFile()

    def test_constructor(self):
        """Test that the constructor for BinnedSpikes sets values as expected."""

        binned_spikes = BinnedSpikes(
            bin_width_in_ms=self.bin_width_in_ms,
            start_time_in_ms=self.start_time_in_ms,
            data=self.data,
        )

        np.testing.assert_array_equal(binned_spikes.data, self.data)

        self.assertEqual(binned_spikes.bin_width_in_ms, self.bin_width_in_ms)
        self.assertEqual(
            binned_spikes.start_time_in_ms, self.start_time_in_ms
        )

        self.assertEqual(binned_spikes.number_of_units, self.number_of_units)
        self.assertEqual(binned_spikes.number_of_bins, self.number_of_bins)

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

        binned_spikes = BinnedSpikes(
            bin_width_in_ms=self.bin_width_in_ms,
            start_time_in_ms=self.start_time_in_ms,
            data=self.data,
            units_region=units_region,
        )

        unit_table_indices = binned_spikes.units_region.data
        unit_table_names = binned_spikes.units_region.table["unit_name"][unit_table_indices]

        expected_names = [unit_name_a, unit_name_c]
        self.assertListEqual(unit_table_names, expected_names)


class TestBinnedSpikesSimpleRoundtrip(TestCase):
    """Simple roundtrip test for BinnedSpikes."""

    def setUp(self):
        self.nwbfile = mock_NWBFile()

        self.path = "test.nwb"

    def tearDown(self):
        remove_test_file(self.path)

    def test_roundtrip_acquisition(self):
        """
        Add a BinnedSpikes to an NWBFile, write it to file, read the file
        and test that the BinnedSpikes from the file matches the original BinnedSpikes.
        """
        # Testing here
        number_of_units = 5
        number_of_bins = 10

        binned_spikes = mock_BinnedSpikes(
            number_of_units=number_of_units,
            number_of_bins=number_of_bins,
        )

        self.nwbfile.add_acquisition(binned_spikes)

        with NWBHDF5IO(self.path, mode="w") as io:
            io.write(self.nwbfile)

        with NWBHDF5IO(self.path, mode="r", load_namespaces=True) as io:
            read_nwbfile = io.read()
            read_binned_spikes = read_nwbfile.acquisition["BinnedSpikes"]
            self.assertContainerEqual(binned_spikes, read_binned_spikes)

            assert read_binned_spikes.number_of_units == number_of_units
            assert read_binned_spikes.number_of_bins == number_of_bins

    def test_roundtrip_processing_module(self):
        binned_spikes = mock_BinnedSpikes()

        ecephys_processinng_module = self.nwbfile.create_processing_module(name="ecephys", description="a description")
        ecephys_processinng_module.add(binned_spikes)

        with NWBHDF5IO(self.path, mode="w") as io:
            io.write(self.nwbfile)

        with NWBHDF5IO(self.path, mode="r", load_namespaces=True) as io:
            read_nwbfile = io.read()
            read_container = read_nwbfile.processing["ecephys"]["BinnedSpikes"]
            self.assertContainerEqual(binned_spikes, read_container)

    def test_roundtrip_with_units_table(self):

        units = mock_Units(num_units=3)
        self.nwbfile.units = units
        region_indices = [0, 2]
        units_region = DynamicTableRegion(
            data=region_indices, table=units, description="region of units table", name="units_region"
        )

        binned_spikes_with_region = mock_BinnedSpikes(units_region=units_region)
        self.nwbfile.add_acquisition(binned_spikes_with_region)

        with NWBHDF5IO(self.path, mode="w") as io:
            io.write(self.nwbfile)

        with NWBHDF5IO(self.path, mode="r", load_namespaces=True) as io:
            read_nwbfile = io.read()
            read_binned_spikes = read_nwbfile.acquisition["BinnedSpikes"]
            self.assertContainerEqual(binned_spikes_with_region, read_binned_spikes)

    def test_data_with_nans(self):
        
        binned_spikes = mock_BinnedSpikes(add_random_nans=True)

        self.nwbfile.add_acquisition(binned_spikes)

        with NWBHDF5IO(self.path, mode="w") as io:
            io.write(self.nwbfile)

        with NWBHDF5IO(self.path, mode="r", load_namespaces=True) as io:
            read_nwbfile = io.read()
            read_binned_spikes = read_nwbfile.acquisition["BinnedSpikes"]
            self.assertContainerEqual(binned_spikes, read_binned_spikes)
