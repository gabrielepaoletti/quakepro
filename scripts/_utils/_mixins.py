"""
@author: Gabriele Paoletti
@e-mail: gabriele.paoletti@uniroma1.it
"""

# --------------------------------------------------------------------------------------------------------
# IMPORTING REQUIRED MODULES
# --------------------------------------------------------------------------------------------------------

import os
import time
import h5py
import warnings

import numpy as np
import pandas as pd

from tqdm.auto import tqdm
from obspy import UTCDateTime

# --------------------------------------------------------------------------------------------------------
# DEFINING CLASSE AND METHODS
# --------------------------------------------------------------------------------------------------------

class _InitMixin:
    """
    A mixin class providing initialization-related utilities.
    """
    @staticmethod
    def _disable_warnings() -> None:
        """
        Disable future warnings.

        Returns
        -------
        None
        """
        warnings.simplefilter(action='ignore', category=FutureWarning)
    

    def _create_directory(self) -> str:
        """
        Create a directory based on the station's name in the current working directory.

        Returns
        -------
        str
            The path to the created directory.
        """
        dir_path = os.path.join(os.getcwd(), self.station.name)
        os.makedirs(dir_path, exist_ok=True)
        return dir_path

class _FetcherMixin:
    """
    A mixin class providing methods to fetch and process seismic waveform data.
    """
    def _download_waveforms(self, event: pd.Series) -> np.ndarray:
        """
        Download waveform data for a given seismic event.

        Parameters
        ----------
        event : pd.Series
            A series containing the event details.

        Returns
        -------
        np.ndarray
            An array containing the waveform data.

        Raises
        ------
        ValueError
            If there are gaps, or the data is not available.
        """
        time.sleep(0.2) # Sleep time to avoid spam-requests
    
        st_raw = self.client.get_waveforms(
            network=self.network,
            station=self.station.name,
            location=self.location,
            channel=self.channel,
            starttime=UTCDateTime(event.trace_start_time),
            endtime=UTCDateTime(event.trace_end_time),
            attach_response=True if self.remove_response else False
        )

        if self.detrend:
            st_raw.detrend(self.detrend)
        
        if self.remove_response:
            st_raw.remove_response(
                inventory=self.station.inventory,
                output=self.remove_response
            )

        if self.resample:
            st_raw.resample(self.resample)
        
        if not st_raw.get_gaps():
            self.station.sampling_rate = st_raw[0].stats.sampling_rate
            trace_length = (pd.to_timedelta(self.trace_len).total_seconds() if isinstance(self.trace_len, str) else self.trace_len) * self.station.sampling_rate
            data = np.stack([trace.data[0:int(trace_length)] for trace in st_raw])
            return data
        
        else:
            raise ValueError()
    
    def _create_dataset(self, file: h5py.File, event: pd.Series, waveform: np.ndarray) -> h5py.Dataset:
        """
        Create and return a dataset in an HDF5 file for storing waveform data of a seismic event.

        Parameters
        ----------
        file : h5py.File
            The HDF5 file object in which the dataset will be created.

        event : pd.Series
            A pandas Series object containing details of the seismic event.

        waveform : np.ndarray
            An array of waveform data associated with the seismic event.

        Returns
        -------
        h5py.Dataset
            The created dataset within the HDF5 file, containing the waveform data. The dataset is named using a combination
            of the station name, network code, and the event ID from the event series.
        """
        return file.create_dataset(
            name=f'{self.station.name}.{self.network}.{event.id}',
            data=waveform
            )
    
    def _generate_attributes(self, event: pd.Series, dataset: h5py.Dataset) -> dict:
        """
        Generate event attributes to be appended.

        This method should be overridden in the class that uses the mixin to provide specific attributes.

        Parameters
        ----------
        event : pd.Series
            A series containing the event details.
            
        dataset : h5py.Dataset
            The HDF5 dataset to retrieve the name of the waveform.

        Returns
        -------
        dict
            A dictionary containing event attributes.
        """
        raise NotImplementedError('Subclasses should implement this method to generate event attributes.')

    def _append_attributes(self, event: pd.Series, dataset: h5py.Dataset) -> None:
        """
        Append attributes to the HDF5 dataset for a seismic event.

        Parameters
        ----------
        event : pd.Series
            A series containing the event details.
            
        dataset : h5py.Dataset
            The HDF5 dataset to retrieve the name of the waveform.

        Returns
        -------
        None
        """
        event_attributes = self._generate_attributes(event, dataset)
        self._attr_list.append(event_attributes)

    def _save_attributes(self) -> None:
        """
        Save the collected attributes from all processed events into a CSV file.

        Returns
        -------
        None
        """
        attributes = pd.DataFrame(self._attr_list)
        attributes.to_csv(f'{self._dir_path}/{self.station.name}_attributes.csv', index=False)
    
    def _create_catalog(self) -> None:
        """
        Main method to create a waveform catalog by processing each event in the seismic catalog.

        Returns
        -------
        None
        """
        with h5py.File(f'{self._dir_path}/{self.station.name}_waveforms.hdf5', 'w') as f:
            for _, event in tqdm(self.catalog.iterrows(), total=self.catalog.shape[0], desc='Downloading waveforms'):
                try:
                    waveform = self._download_waveforms(event)
                except Exception as e:
                    tqdm.write(f'Waveform not found for event ID-{event.id}.')
                    continue
                
                dataset = self._create_dataset(f, event, waveform)
                self._append_attributes(event, dataset)
            
            self._save_attributes()