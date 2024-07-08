"""
@author: Gabriele Paoletti
@e-mail: gabriele.paoletti@uniroma1.it
"""

# --------------------------------------------------------------------------------------------------------
# IMPORTING REQUIRED MODULES
# --------------------------------------------------------------------------------------------------------

import obspy

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