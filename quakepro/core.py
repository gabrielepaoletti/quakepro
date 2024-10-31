import h5py
import pandas as pd

from quakepro.components.dataset import WaveformDataset


def load_dataset(
        hdf5_path: str,
        attrs_path: str
    ) -> tuple[h5py.File, pd.DataFrame]:
    """
    Load seismic waveform data and associated attributes from specified files.

    Parameters
    ----------
    hdf5_path : str
        Path to the HDF5 file containing waveform data.
    attrs_path : str
        Path to the CSV file containing waveform attributes.

    Returns
    -------
    tuple
        A tuple containing:
            - h5py.File : The HDF5 file object with waveform data.
            - pd.DataFrame : DataFrame with attributes, including parsed datetime columns.
    """
    wavs = h5py.File(hdf5_path, 'r')

    attrs = pd.read_csv(
        attrs_path,
        parse_dates=['trace_start_time', 'source_origin_time']
    )

    return WaveformDataset(wavs, attrs)
