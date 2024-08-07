"""
@author: Gabriele Paoletti
@e-mail: gabriele.paoletti@uniroma1.it
"""

# --------------------------------------------------------------------------------------------------------
# IMPORTING REQUIRED MODULES
# --------------------------------------------------------------------------------------------------------

import h5py
import argparse

import numpy as np
import pandas as pd

from tqdm.auto import tqdm
from obspy.taup import TauPyModel
from obspy.clients.fdsn import Client

from _utils._mixins import _InitMixin, _FetcherMixin
from _utils._station import _Station

# --------------------------------------------------------------------------------------------------------
# DEFINING CLASSE AND METHODS
# --------------------------------------------------------------------------------------------------------

class CSVFetcher(_InitMixin, _FetcherMixin):
    def __init__(self, client: str, network: str, station: str, location: str, channel: str, catalog_path: str, model: str, time_before_p: float, time_after_p: float, detrend: str=None, resample: float=None, remove_response: str =None) -> None:
        """
        Initialize the CSVFetcher for downloading seismic waveforms.

        Parameters
        ----------
        client : str
            Client code for the FDSN data service. This is typically an abbreviation of the data provider.

        network : str
            Seismic network to retrieve data from. Network codes are standardized identifiers for networks

        station : str
            The station code to retrieve data for. This identifies a specific seismic station within the network.

        location : str
            Location code within the station. This can be used to identify different sensors or positions at the same station.

        channel : str
            Channel code(s) specifying the types of data to retrieve. Channels are typically identified by three characters.

        model : str
            Earth velocity model for travel time calculations.

        time_before_p : float
            Time in seconds before P-wave arrival to start the trace.

        time_after_p : float
            Time in seconds after P-wave arrival to end the trace.

        catalog_path : str
            Path to the earthquake catalog CSV file.

        detrend : str, optional
            Method to be used for detrending the data. Default is ``'linear'``.

        resample : float, optional
            The new sampling rate in Hz to resample the waveform data. This can be used to standardize the sampling rate across different datasets. Default is ``None``, meaning no resampling will occur.

        remove_risponse : str, optional
            Specifies whether to remove the instrument response from the data and convert to a specified output. Default is ``None``, meaning no response removal will occur.

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
        self.trace_len = time_before_p + time_after_p
        self.catalog = self._load_catalog(catalog_path)
        self.model = TauPyModel(model)
        self.detrend = detrend
        self.resample = resample
        self.remove_response = remove_response

        self._dir_path = self._create_directory()
        self._attr_list = []
        
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
        origin_times = self.catalog.time
        arrival_times = origin_times + pd.to_timedelta(self.catalog.p_travel_time_s, unit='seconds')
        self.catalog['trace_start_time'] = arrival_times - pd.to_timedelta(self.time_before_p, unit='seconds')
        self.catalog['trace_end_time'] = arrival_times + pd.to_timedelta(self.time_after_p, unit='seconds')

    def _generate_attributes(self, event: pd.Series, dataset: h5py.Dataset) -> dict:
        """
        Generate event attributes specific to CSVFetcher.

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
        return {
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
    
    def create_waveform_catalog(self) -> None:
        """
        Main method to create a waveform catalog by processing each event in the seismic catalog.

        Returns
        -------
        None
        """
        self._calculate_p_travel_times()
        self._calculate_trace_times()
        self._create_catalog()

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
        help='Client code for the FDSN data service. This is typically an abbreviation of the data provider.'
    )
    parser.add_argument(
        '-n', '--network', type=str, required=True, 
        help='Seismic network to retrieve data from. Network codes are standardized identifiers for networks'
    )
    parser.add_argument(
        '-s', '--station', type=str, required=True,
        help='The station code to retrieve data for. This identifies a specific seismic station within the network.'
    )
    parser.add_argument(
        '-l', '--location', type=str, required=True,
        help='Location code within the station. This can be used to identify different sensors or positions at the same station.'
    )
    parser.add_argument(
        '-c', '--channel', type=str, required=True,
        help='Channel code(s) specifying the types of data to retrieve. Channels are typically identified by three characters.'
    )
    parser.add_argument(
        '-m', '--model', type=str, required=True,
        help='Earth velocity model for travel time calculations.'
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
        help='Method to be used for detrending the data. Default is "linear".'
    )
    parser.add_argument(
        '--resample', type=float, required=False,
        help='The new sampling rate in Hz to resample the waveform data. This can be used to standardize the sampling rate across different datasets.'
    )
    parser.add_argument(
        '--remove_response', required=False,
        choices=['VEL', 'ACC', 'DISP', 'None'],
        help='Specifies whether to remove the instrument response from the data and convert to a specified output.'
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
    fetcher = CSVFetcher(
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