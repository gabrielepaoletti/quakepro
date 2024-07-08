QUAKEPRO Fetchers (QPFs)
========================

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

        .. raw:: html
            <br>

        - **Attributes CSV file**, that contains metadata for each seismic event/waveform and the station itself.
        - **HDF5 waveforms file**, that stores all the waveforms as ``numpy.ndarray`` objects. The file is structured into datasets, with each dataset named according to the trace name.
            
        .. code-block:: text

            /<station_name>/
            ├── <station_name>_attributes.csv
            └── <station_name>_waveforms.hdf5

        The datasets in the HDF5 file are linked to the metadata in the CSV file through the ``trace_name`` column. This allows users to easily pair waveform data with their corresponding event and station metadata.

        .. warning::
            It is important not to rename these files to ensure proper integration with `processing <https://quakepro.readthedocs.io/en/latest/documentation/modules/processing.html>`_ and `visualization <https://quakepro.readthedocs.io/en/latest/documentation/modules/plot.html>`_ modules. You can safely rename the directory, but changing the filenames inside it may disrupt the functionality of other functions and methods.

.. option:: $ qpf-int <subcommand> [options]

    Download seismic waveforms using FDSN web services for specified time intervals, allowing you to define the length of the waveform segments and the sampling frequency.

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

        **\--start_date** : *str*
             The start date for the data retrieval period in ``'YYYY-MM-DD'`` format. This indicates the beginning of the time span for which data will be retrieved.
        
        **\--end_date** : *str*
            The end date for the data retrieval period in ``'YYYY-MM-DD'`` format. This indicates the end of the time span for which data will be retrieved.

        **\--trace_len** : *str*
            Length of the trace to be downlaoded. This specifies the duration of each individual waveform segment to be retrieved.

            .. note::
                This parameter must be passed as a Pandas frequency string (e.g., ``'1T'`` for 1 minute, ``'1D'`` for 1 day).

        **\--interval** : *str*
            Interval between each data point. This determines how often the waveform data should be sampled within the specified date range.

            .. note::
                This parameter must be passed as a Pandas frequency string (e.g., ``'1T'`` for 1 minute, ``'1D'`` for 1 day).   
        
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

        .. raw:: html
            <br>

        - **Attributes CSV file**, that contains metadata for each seismic event/waveform and the station itself.
        - **HDF5 waveforms file**, that stores all the waveforms as ``numpy.ndarray`` objects. The file is structured into datasets, with each dataset named according to the trace name.
            
        .. code-block:: text

            /<station_name>/
            ├── <station_name>_attributes.csv
            └── <station_name>_waveforms.hdf5

        The datasets in the HDF5 file are linked to the metadata in the CSV file through the ``trace_name`` column. This allows users to easily pair waveform data with their corresponding event and station metadata.

        .. warning::
            It is important not to rename these files to ensure proper integration with `processing <https://quakepro.readthedocs.io/en/latest/documentation/modules/processing.html>`_ and `visualization <https://quakepro.readthedocs.io/en/latest/documentation/modules/plot.html>`_ modules. You can safely rename the directory, but changing the filenames inside it may disrupt the functionality of other functions and methods.



