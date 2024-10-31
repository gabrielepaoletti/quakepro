import h5py
import pandas as pd

from quakepro.components.waveform import Waveform


class WaveformDataset:
    """
    A dataset class for managing and accessing seismic waveform data and 
    associated metadata.

    Parameters
    ----------
    wavs : h5py.File
        An HDF5 file containing the seismic waveforms.
    attrs : pd.DataFrame
        A DataFrame containing attributes associated with each waveform.
    
    Attributes
    ----------
    waveforms : list[Waveform]
        List of Waveform objects with data and attributes.
    transformations : list[str]
        List of transformations applied to the dataset.
    """

    def __init__(self, wavs: h5py.File, attrs: pd.DataFrame):
        self.waveforms = [
            Waveform(wavs[trace_name][()], attrs.iloc[idx])
            for idx, trace_name in enumerate(wavs.keys())
        ]

    def apply(self, method_name: str, *args, **kwargs) -> None:
        """
        Apply a specified method to all Waveform objects in the dataset.

        Parameters
        ----------
        method_name : str
            The name of the method to apply to each Waveform.
        *args
            Positional arguments to pass to the method.
        **kwargs
            Keyword arguments to pass to the method.

        Raises
        ------
        AttributeError
            If a Waveform object does not have the specified method.
        """
        for wf in self.waveforms:
            if not hasattr(wf, method_name):
                raise AttributeError(
                    f"'{type(wf).__name__}' object has no method '{method_name}'"
                )
            method = getattr(wf, method_name)
            method(*args, **kwargs)

    def __len__(self) -> int:
        """
        Return the number of waveforms in the dataset.

        Returns
        -------
        int
            The number of waveforms.
        """
        return len(self.waveforms)

    def __repr__(self) -> str:
        """
        Return a string representation of the WaveformDataset.

        Returns
        -------
        str
            String representation of the dataset.
        """
        return f'WaveformDataset(\n  len={len(self.waveforms)}\n)'