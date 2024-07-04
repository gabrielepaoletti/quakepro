"""
@author: Gabriele Paoletti
@e-mail: gabriele.paoletti@uniroma1.it
"""

# --------------------------------------------------------------------------------------------------------
# IMPORTING REQUIRED MODULES
# --------------------------------------------------------------------------------------------------------

import glob
import h5py
import shutil

import numpy as np
import pandas as pd

from tqdm.auto import tqdm
from scipy.signal import butter, sosfilt, sosfiltfilt, get_window

from typing import Tuple, Union

# --------------------------------------------------------------------------------------------------------
# DEFINING CLASSES AND METHODS
# --------------------------------------------------------------------------------------------------------

class Processor:
    def __init__(self, path: str) -> None:
        """
        Initialize the SignalProcessor with the provided path.

        Parameters
        ----------
        path : str
            The path to the directory containing the HDF5 and CSV files.
        
        Returns
        -------
        None
        """
        self.wavs, self.attr = self._locate_files(path)
    
    def _locate_files(self, path: str) -> Tuple[h5py.File, pd.DataFrame]:
        """
        Locate and load the HDF5 and CSV files from the given path.

        Parameters
        ----------
        path : str
            The path to the directory containing the HDF5 and CSV files.

        Returns
        -------
        Tuple[h5py.File, pd.DataFrame]
            A tuple containing the HDF5 file object and the CSV data as a DataFrame.
        """
        original_file = glob.glob(f'{path}/*.hdf5')[0]
        copy_file = original_file.replace('.hdf5', '_copy.hdf5')
        shutil.copyfile(original_file, copy_file)
        
        file = h5py.File(copy_file, 'r+')
        attr = pd.read_csv(glob.glob(f'{path}/*.csv')[0])
        return file, attr
    
    def taper(self, window_type: str, *params) -> None:
        """
        Apply tapering to all waveforms in the HDF5 file.

        .. note::
            If you wish to explore available tapering window options, along with their ``*params``, consult the ``scipy.signal.get_window`` documentation available at `SciPy Docs <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.get_window.html>`_.
    
        Parameters
        ----------
        window_type : str
                The type of window to create. This defines the shape of the tapering window to be applied to each waveform.

        *params : tuple, optional
            Additional parameters to pass to the window function. These parameters vary depending on the window type selected.

        Returns
        -------
        None
        """
        for trace_name in tqdm(iterable=self.attr['trace_name'], desc='Applying taper'):
            signals = self.wavs[trace_name][:]
            tapered_signals = np.zeros_like(signals)
            
            for i, signal in enumerate(signals):
                window = get_window((window_type, *params), len(signal)) if params else get_window(window_type, len(signal))
                tapered_signals[i] = signal * window
            
            self.wavs[trace_name][:] = tapered_signals

    def filter(self, filter_type: str, cutoff: Union[int, list], order: int = 5, zero_phase: bool=True) -> None:
        """
        Apply filtering to all waveforms in the HDF5 file.

        Parameters
        ----------
        filter_type : str
            The type of filter to apply. This can be ``'lowpass'``, ``'highpass'``, ``'bandpass'``, or ``'bandstop'``.

        cutoff : Union[int, list]
            The cutoff frequency or frequencies for the filter. For ``'lowpass'`` and ``'highpass'`` filters, this should be a single value. For ``'bandpass'`` and ``'bandstop'`` filters, this should be a list of two values ``[low_cutoff, high_cutoff]``.

        order : int, optional
            The order of the filter. Higher order filters have a steeper roll-off. Default is ``5``.
            
        zero_phase : bool, optional
             If ``True``, apply zero-phase filtering using ``sosfiltfilt()``, which applies the filter forward and backward to eliminate phase distortion. If ``False``, apply standard filtering using ``sosfilt()``. Default is ``True``.

        Returns
        -------
        None
        """
        nyq = 0.5 * self.attr.receiver_sampling_rate_hz[0].item()
        normal_cutoff = [c / nyq for c in cutoff] if isinstance(cutoff, list) else cutoff / nyq
        sos = butter(order, normal_cutoff, btype=filter_type, output='sos')
        
        for trace_name in tqdm(iterable=self.attr['trace_name'], desc='Applying filter'):
            signals = self.wavs[trace_name][:]
            filtered_signals = np.zeros_like(signals)
            
            for i, signal in enumerate(signals):
                if zero_phase:
                    filtered_signals[i] = sosfiltfilt(sos, signal)
                else:
                    filtered_signals[i] = sosfilt(sos, signal)
            
            self.wavs[trace_name][:] = filtered_signals