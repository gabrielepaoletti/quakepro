"""
This script is designed to automate the process of downloading seismic waveforms from a CSV earthquake catalog.

Usage:
To run the scipt to download data from a certain gatalog, use the command line to navigate to the script's directory and execute it as follows:

$ qpf-csv -p "INGV" -n "IV" -s "MMO1" -l "*" -c "EH*" -m "iasp91" --time_before_p 5 --time_after_p 15 --catalog_path "path_to_your_catalog.csv"

Note:
The script requires an internet connection to access the online data repositories.

@author: Gabriele Paoletti
@e-mail: gabriele.paoletti@uniroma1.it
"""

# --------------------------------------------------------------------------------------------------------
# IMPORTING REQUIRED MODULES
# --------------------------------------------------------------------------------------------------------

import os
import h5py
import time
import obspy
import warnings
import argparse

import numpy as np
import pandas as pd

from tqdm.auto import tqdm
from obspy import UTCDateTime
from obspy.taup import TauPyModel
from obspy.clients.fdsn import Client

from typing import Tuple

# --------------------------------------------------------------------------------------------------------
# DEFINING CLASSES AND METHODS
# --------------------------------------------------------------------------------------------------------

class _Station:
    def __init__(self, client: str, network: str, name: str) -> None:
        """
        Initialize a Station object with client, network, and name details.

        Parameters
        ----------
        client : str
            The identifier for the seismic data service client.

        network : str
            The seismic network code.

        name : str
            The name of the station within the network.

        Returns
        -------
        None
        """
        self.name = name
        self.client = Client(client)
        self.network = network
        self.inventory ,self.longitude, self.latitude, self.elevation = self._get_station_metadata()

    def _get_station_metadata(self) -> Tuple[obspy.Inventory, float, float, int]:
        """
        Retrieve the geographic metadata for the station.

        Returns
        -------
        Tuple[obspy.Inventory, float, float, int]
            A tuple containing the inventory object, longitude, latitude, and elevation of the station.
        """
        inventory = self.client.get_stations(network=self.network, station=self.name)
        for network in inventory:
            for station in network:
                return inventory, station.longitude, station.latitude, station.elevation

class WaveformFetcher:
    def __init__(self, client: str, network: str, station: str, location: str, channel: str, catalog_path: str, model: str, time_before_p: float, time_after_p: float, detrend: str=None, resample: float=None, remove_response: str =None) -> None:
        """
        Initialize the Waveform Fetcher for downloading seismic waveforms.

        Parameters
        ----------
        client : str
            The identifier for the seismic data service client.

        network : str
            The network code to identify the seismic network.

        station : str
            The station code to retrieve data for.

        location : str
            The location code within the station.

        channel : str
            The channel code(s) indicating types of data (e.g., 'HH*').

        catalog_path : str
            Path to the catalog file containing earthquake events data.

        model : str
            The earth model to use for travel time calculations.

        time_before_p : float
            Time in seconds before the predicted P-wave arrival to start the trace.

        time_after_p : float
            Time in seconds after the predicted P-wave arrival to end the trace.

        detrend : str, optional
            Method used for detrending data.

        resample : float, optional
            New sampling rate to resample the waveform data.

        remove_risponse : str, optional
            Whether to remove the instrument response to the waveform data (e.g. 'VEL', 'ACC' or 'DISP').

        Returns
        -------
        None
        """
        self.client = Client(client)
        self.network = network
        self.station = _Station(client, network, station)
        self.location = location
        self.channel = channel
        self.time_before_p = time_before_p
        self.time_after_p = time_after_p
        self.catalog = self._load_catalog(catalog_path)
        self.__dir_path = self._create_directory()
        self.model = TauPyModel(model)
        self.detrend = detrend
        self.resample = resample
        self.remove_response = remove_response
        self.__attr_list = []
        
    @staticmethod
    def _disable_warnings() -> None:
        """
        Disable future warnings.

        Returns
        -------
        None
        """
        warnings.simplefilter(action='ignore', category=FutureWarning)
    
    def _load_catalog(self, path: str) -> pd.DataFrame:
        """
        Load a seismic event catalog from a CSV file.

        Parameters
        ----------
        path : str
            Path to the catalog CSV file.

        Returns
        -------
        pd.DataFrame
            A DataFrame containing the loaded catalog.
        """
        catalog = pd.read_csv(path)
        catalog.time = pd.to_datetime(catalog.time)
        return catalog
    
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
    
    def _calculate_p_travel_times(self) -> None:
        """
        Calculate the P-wave travel times for all events in the catalog using a standard velocity model.

        Returns
        -------
        None
        """
        self.catalog['p_travel_time_s'] = None
        for idx, event in tqdm(self.catalog.iterrows(), total=self.catalog.shape[0], desc='Calculating P-wave travel times'):
            travel_times = self.model.get_travel_times_geo(
                source_depth_in_km=event.depth,
                source_latitude_in_deg=event.lat,
                source_longitude_in_deg=event.lon,
                receiver_latitude_in_deg=self.station.latitude,
                receiver_longitude_in_deg=self.station.longitude
            )
            if travel_times:
                self.catalog.at[idx, 'p_travel_time_s'] = round(travel_times[0].time, 5)
            else:
                self.catalog.at[idx, 'p_travel_time_s'] = np.nan
    
    def _calculate_trace_times(self) -> None:
        """
        Calculate the start and end times for the waveform traces based on the P-wave travel times.

        Returns
        -------
        None
        """
        origin_times = self.catalog.time.apply(UTCDateTime)
        arrival_times = origin_times + self.catalog.p_travel_time_s
        self.catalog['trace_start_time'] = arrival_times - self.time_before_p
        self.catalog['trace_end_time'] = arrival_times + self.time_after_p

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
            starttime=event.trace_start_time,
            endtime=event.trace_end_time,
            attach_response=self.attach_response
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
            trace_length = (self.time_before_p + self.time_after_p)*self.station.sampling_rate
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
        event_attributes = {
                'trace_name': dataset.name[1:],
                'trace_start_time': event.trace_start_time,
                'rec_network': self.network,
                'rec_name': self.station.name,
                'rec_type': self.channel[0:2],
                'rec_latitude_deg': self.station.latitude,
                'rec_longitude_deg': self.station.longitude,
                'rec_elevation_m': self.station.elevation,
                'rec_sampling_rate_hz': self.station.sampling_rate,
                'src_id': event.id,
                'src_origin_time': event.time,
                'src_latitude_deg': event.lon,
                'src_longitude_deg': event.lat,
                'src_depth_km': event.depth,
                'src_magnitude': event.magnitude,
                'p_travel_sec': event.p_travel_time_s
        }
        self.__attr_list.append(event_attributes)
    
    def _save_attributes(self) -> None:
        """
        Save the collected attributes from all processed events into a CSV file.

        Returns
        -------
        None
        """
        attributes = pd.DataFrame(self.__attr_list)
        attributes.to_csv(f'{self.__dir_path}/{self.station.name}_attributes.csv', index=False)
    
    def create_waveform_catalog(self) -> None:
        """
        Main method to create a waveform catalog by processing each event in the seismic catalog.

        Returns
        -------
        None
        """
        self._calculate_p_travel_times()
        self._calculate_trace_times()

        with h5py.File(f'{self.__dir_path}/{self.station.name}_waveforms.hdf5', 'w') as f:
            for _, event in tqdm(self.catalog.iterrows(), total=self.catalog.shape[0], desc='Downloading waveforms'):
                try:
                    waveform = self._download_waveforms(event)
                except Exception as e:
                    tqdm.write(f'Waveform not found for event ID-{event.id}.')
                    continue
                
                dataset = self._create_dataset(f, event, waveform)
                self._append_attributes(event, dataset)
            
            self._save_attributes()

# --------------------------------------------------------------------------------------------------------
# DEFINING FUNCTIONS
# --------------------------------------------------------------------------------------------------------

def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns
    -------
    Namespace
        A namespace populated with parsed arguments.
    """
    parser = argparse.ArgumentParser()

    # Mandatory arguments
    parser.add_argument(
        '-p', '--client', type=str, required=True,
        choices=['AUSPASS', 'BGR', 'EIDA', 'EMSC', 'ETH', 'GEOFON', 'GEONET', 'GFZ', 'ICGC', 'IESDMC', 'INGV', 'IPGP', 'IRIS', 'IRISPH5', 'ISC', 'KNMI', 'KOERI', 'LMU', 'NCEDC', 'NIEP', 'NOA', 'ODC', 'ORFEUS', 'RASPISHAKE', 'RESIF', 'RESIFPH5', 'SCEDC', 'TEXNET', 'UIB-NORSAR', 'USGS', 'USP'],
        help='Client code for the FDSN data service.'
    )
    parser.add_argument(
        '-n', '--network', type=str, required=True, 
        help='Network code to identify the seismic network.'
    )
    parser.add_argument(
        '-s', '--station', type=str, required=True,
        help='Station code to retrieve data for.'
    )
    parser.add_argument(
        '-l', '--location', type=str, required=True,
        help='Location code within the station.'
    )
    parser.add_argument(
        '-c', '--channel', type=str, required=True,
        help='Channel code(s) indicating types of data.'
    )
    parser.add_argument(
        '-m', '--model', type=str, required=True,
        help='Earth model for travel time calculations.'
    )
    parser.add_argument(
        '--time_before_p', type=float, required=True,
        help='Time in seconds before P-wave arrival to start the trace.'
    )
    parser.add_argument(
        '--time_after_p', type=float, required=True,
        help='Time in seconds after P-wave arrival to end the trace.'
    )
    parser.add_argument(
        '--catalog_path', type=str, required=True,
        help='Path to the earthquake catalog CSV file.'
    )

    # Optional arguments
    parser.add_argument(
        '--detrend', type=str, required=False,
        choices=['simple', 'linear', 'constant', 'polynomial', 'spline', 'None'], default='linear', 
        help='Method used for detrending data (default: linear).'
    )
    parser.add_argument(
        '--resample', type=float, required=False,
        help='New sampling rate in Hz to resample the waveform data.'
    )
    parser.add_argument(
        '--remove_response', required=False,
        choices=['VEL', 'ACC', 'DISP', 'None'],
        help='Remove the instrument response and convert to the specified output.'
    )

    return parser.parse_args()

def main() -> None:
    """
    Main function to run the waveform download process.

    Returns
    -------
    None
    """
    args = parse_arguments()
    fetcher = WaveformFetcher(
        client=args.client,
        network=args.network,
        station=args.station,
        location=args.location,
        channel=args.channel,
        catalog_path=args.catalog_path,
        model=args.model,
        time_before_p=args.time_before_p,
        time_after_p=args.time_after_p,
        detrend=args.detrend,
        resample=args.resample,
        remove_response=args.remove_response,
    )

    fetcher.create_waveform_catalog()

# --------------------------------------------------------------------------------------------------------
# MAIN EXECUTION
# --------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    main()