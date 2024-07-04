QUAKEPRO Fetcher (QPF) - CSV
===============================

.. option:: $ qpf-csv <subcommand> [options]

    Download seismic waveforms using FDSN web services from a pre-built CSV earthquake catalog.

    .. warning::
        For the script to work properly, it is important that the CSV input columns are formatted as explained in the `tutorial <https://quakepro.readthedocs.io/en/latest/user_guide/tutorials.html>`_.

    :Subcommands:
        **-p, \--client** : *str*
            Client code for the FDSN data service. This is typically an abbreviation of the data provider.

        **-n, \--network** : *str*
            Seismic network to retrieve data from. Network codes are standardized identifiers for networks
        
        **-s, \--station** : *str*
            The station code to retrieve data for. This identifies a specific seismic station within the network.

        **-l, \--location** : *str*
            Location code within the station. This can be used to identify different sensors or positions at the same station.

        **-c, \--channel** : *str*
            Channel code(s) specifying the types of data to retrieve. Channels are typically identified by three characters.

        **-m, \--model** : *str*
            Earth velocity model for travel time calculations.

            .. note::
                Custom built models can be initialized by specifying an absolute path to a model in ObsPy’s ``.npz`` model format instead of just a model name.

        **\--time_before_p** : *float*
            Time in seconds before P-wave arrival to start the trace.

        **\--time_after_p** : *float*
            Time in seconds after P-wave arrival to end the trace.

        **\--catalog_path** : *str*
            Path to the earthquake catalog CSV file.
        
        **\--detrend** : *str, optional*
            Method to be used for detrending the data. Default is ``linear``.
        
        **\--resample** : *float, optional*
            The new sampling rate in Hz to resample the waveform data. This can be used to standardize the sampling rate across different datasets. Default is ``None``, meaning no resampling will occur.

        **\--remove_response** : *str, optional*
             Specifies whether to remove the instrument response from the data and convert to a specified output. Default is ``None``, meaning no response removal will occur.
    
    :Options:
        Each subcommand has its own set of options. Use ``qpf-csv <subcommand> --help`` to see which of the following options apply to any of the subcommands listed above.

    :Returns:
        This script generates a directory (in the path from which this script was launched) named after the seismic station from which the data was downloaded. Inside this directory, you will find two primary files:

        - **Attributes CSV file**, that contains metadata for each seismic event/waveform and the station itself.
        - **HDF5 waveforms file**, that stores all the waveforms as ``numpy.ndarray`` objects. The file is structured into datasets, with each dataset named according to the trace name. This enables easy identification and matching of waveforms with their respective metadata.
        
        .. code-block:: text

            /<station_name>/
            ├── <station_name>_attributes.csv
            └── <station_name>_waveforms.hdf5

        The datasets in the HDF5 file are linked to the metadata in the CSV file through the ``trace_name`` column. This allows users to easily pair waveform data with their corresponding event and station metadata.

        .. warning::
            It is important not to rename these files to ensure proper integration with `processing <https://quakepro.readthedocs.io/en/latest/documentation/modules/processing.html>`_ and `visualization <https://quakepro.readthedocs.io/en/latest/documentation/modules/visualization.html>`_ modules. You can safely rename the directory, but changing the filenames inside it may disrupt the functionality of other functions and methods.


        


