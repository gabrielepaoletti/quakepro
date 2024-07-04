QUAKEPRO Fetcher (QPF) from CSV
===============================

.. option:: $ qpf-csv <subcommand> [options]

    Download seismic waveforms using FDSN web services from a CSV earthquake catalog.

    .. warning::
        For the script to work properly, it is important that the CSV input columns are formatted as explained in the `tutorial <https://quakepro.readthedocs.io/en/latest/user_guide/tutorials.html>`_.

    :Subcommands:
        **-p, \--client** : *str*
            Client code for the FDSN data service.

        **-n, \--network** : *str*
            Network code to identify the seismic network.
        
        **-s, \--station** : *str*
            Station code to retrieve data for.

        **-l, \--location** : *str*
            Location code within the station.

        **-c, \--channel** : *str*
            Channel code(s) indicating types of data.

        **-m, \--model** : *str*
            Earth velocity model for travel time calculations.

        **\--time_before_p** : *float*
            Time in seconds before P-wave arrival to start the trace.

        **\--time_after_p** : *float*
            Time in seconds after P-wave arrival to end the trace.

        **\--catalog_path** : *str*
            Path to the earthquake catalog CSV file.
        
        **\--detrend** : *str, optional*
            Method used for detrending data. Default is ``linear``.
        
        **\--resample** : *float, optional*
            New sampling rate in Hz to resample the waveform data. Default is ``None``.

        **\--remove_response** : *str, optional*
            Remove the instrument response and convert to the specified output. Default is ``None``.
    
    :Options:
        Each subcommand has its own set of options. Use ``qpf-csv <subcommand> --help`` to see which of the following options apply to any of the subcommands listed above.
        


