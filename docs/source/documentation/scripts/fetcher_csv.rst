Download waveforms from CSV
===========================

.. program:: qpf-csv

::
    qpf-csv <subcommand> [options]

.. describe:: -p, --provider
    Client code for the FDSN data service.

.. describe:: -n, --network
    Network code to identify the seismic network.

.. describe:: -s, --station
    Station code to retrieve data for.

.. describe:: -l, --location
    Location code within the station.

.. describe:: -c, --channel
    Channel code(s) indicating types of data.

.. describe:: -m, --model
    Earth velocity model for travel time calculations.

.. describe:: --time_before_p
    Time in seconds before P-wave arrival to start the trace.

.. describe:: --time_after_p
    Time in seconds after P-wave arrival to end the trace.

.. describe:: --catalog_path
    Path to the earthquake catalog CSV file.

.. describe:: --detrend
    Method used for detrending data. Default is ``linear``.

.. describe:: --resample
    New sampling rate in Hz to resample the waveform data.

.. describe:: --remove_response
    Remove the instrument response and convert to the specified output.