"""
@author: Gabriele Paoletti
@e-mail: gabriele.paoletti@uniroma1.it
"""

# --------------------------------------------------------------------------------------------------------
# IMPORTING REQUIRED MODULES
# --------------------------------------------------------------------------------------------------------

import h5py
import argparse

import pandas as pd

from obspy.clients.fdsn import Client

from _utils._mixins import _InitMixin, _FetcherMixin
from _utils._station import _Station

# --------------------------------------------------------------------------------------------------------
# DEFINING CLASSES AND METHODS
# --------------------------------------------------------------------------------------------------------

class INTFetcher(_InitMixin, _FetcherMixin):
    def __init__(self, client: str, network: str, station: str, location: str, channel: str, start_date: str, end_date: str, trace_len: float, interval: str, detrend: str=None, resample: float=None, remove_response: str =None) -> None:
        """
        Initialize the INTCSVFetcher for downloading seismic waveforms.

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

        start_date : str
             The start date for the data retrieval period in ``'YYYY-MM-DD'`` format. This indicates the beginning of the time span for which data will be retrieved.

        end_date : str
            The end date for the data retrieval period in ``'YYYY-MM-DD'`` format. This indicates the end of the time span for which data will be retrieved.

        trace_len : float
            Length of the trace to be downlaoded. This specifies the duration of each individual waveform segment to be retrieved.

            .. note::
                This parameter must be passed as a Pandas frequency string (e.g., ``'1T'`` for 1 minute, ``'1D'`` for 1 day).

        interval : str
            Interval between each data point. This determines how often the waveform data should be sampled within the specified date range.

            .. note::
                This parameter must be passed as a Pandas frequency string (e.g., ``'1T'`` for 1 minute, ``'1D'`` for 1 day).

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
        self.start_date = start_date
        self.end_date = end_date
        self.trace_len = trace_len
        self.interval = interval
        self.catalog = self._generate_catalog()
        self.detrend = detrend
        self.resample = resample
        self.remove_response = remove_response
        
        self._dir_path = self._create_directory()
        self._attr_list = []

    def _generate_catalog(self) -> pd.DataFrame:
        """
        Generate a ``pd.DataFrame`` with a column ``'time'`` containing datetimes at specified intervals.

        Returns
        -------
        pd.DataFrame
            DataFrame with a ``'time'`` column.
        """
        date_range = pd.date_range(start=self.start_date, end=self.end_date, freq=self.interval)
        ids = pd.Series(range(100000000, 100000000 + len(date_range)))
        df = pd.DataFrame({'id': ids, 'trace_start_time': date_range})
        df['trace_end_time'] = df['trace_start_time'] + pd.to_timedelta(self.trace_len)
        return df
    
    def _generate_attributes(self, event: pd.Series, dataset: h5py.Dataset) -> dict:
        """
        Generate event attributes specific to INTFetcher.

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
        }

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
        '--start_date', type=str, required=True,
        help='The start date for the data retrieval period in YYYY-MM-DD format. This indicates the beginning of the time span for which data will be retrieved.'
    )
    parser.add_argument(
        '--end_date', type=str, required=True,
        help='The end date for the data retrieval period in YYYY-MM-DD format. This indicates the end of the time span for which data will be retrieved.'
    )
    parser.add_argument(
        '--trace_len', type=str, required=True,
        help='Length of the trace to be downlaoded. This specifies the duration of each individual waveform segment to be retrieved.'
    )
    parser.add_argument(
        '--interval', type=str, required=True,
        help='Interval between each data point. This determines how often the waveform data should be sampled within the specified date range.'
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
    fetcher = INTFetcher(
        client=args.client,
        network=args.network,
        station=args.station,
        location=args.location,
        channel=args.channel,
        start_date=args.start_date,
        end_date=args.end_date,
        trace_len=args.trace_len,
        interval=args.interval,
        detrend=args.detrend,
        resample=args.resample,
        remove_response=args.remove_response
    )

    fetcher._create_catalog()

# --------------------------------------------------------------------------------------------------------
# MAIN EXECUTION
# --------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    main()