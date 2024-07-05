How to download waveforms from a CSV earthquake catalog
=======================================================

In this tutorial, you will learn how to efficiently download seismic waveforms using QUAKEPRO from a CSV-formatted earthquake catalog. This guide is designed to assist you in preparing your CSV file correctly and using it to retrieve the necessary waveform data seamlessly.

CSV Catalog Formatting
----------------------

To ensure that the download software provided by QUAKEPRO functions correctly, it is necessary to format the earthquake catalog CSV file properly. The CSV file should contain the following columns, named exactly as specified (pay attention to capitalization):

- ``id``, the unique identifier for the earthquake.
- ``time``, the origin time of the earthquake, in a format readable by ``pandas``.
- ``lon``, the longitude of the earthquake, expressed in degrees.
- ``lat``, the latitude of the earthquake, expressed in degrees.
- ``depth``, the depth of the earthquake, expressed in kilometers. It is preferable that the number is positive.
- ``magnitude``, the magnitude of the earthquake.

Here is an example of how your CSV file should look:

.. code-block:: csv

    id,time,lon,lat,depth,magnitude
    100588130,2016-08-15 20:00:36.166,13.11558,42.80242,6.609,1.26
    100588131,2016-08-15 20:04:47.245,13.11725,42.80427,6.838,0.72
    ...
    101373171,2017-08-15 22:19:29.229,13.02917,42.84478,8.171,0.33

.. note::
    It is not necessary for the CSV file to contain only these columns; it can include additional ones. However, these specific columns must be present and named correctly as they are required for the download software to function.

Waveform download
-----------------

Once the CSV file is prepared, you can download the waveforms by opening the command prompt and running the download script (ensure QUAKEPRO is `installed <https://quakepro.readthedocs.io/en/latest/user_guide/installation.html>`_ on your device):

.. code-block:: bash

    qpf-csv -p INGV -n IV -s MMO1 -c EH* -l * -m iasp91 --time_before_p 10 --time_after_p 20 --catalog_path "<path>/<catalog_name>.csv"

.. note::
    In this command, wildcards are used to specify multiple options conveniently. For example, ``EH*`` indicates that all channels starting with ``EH`` should be downloaded. This flexibility allows you to customize the command to suit your specific needs.

This command will download 30-second-windowed (10 seconds before and 20 seconds after the P-wave arrival) three-channel waveforms for all events in the CSV catalog from MMO1 seismic station.

When the software is running, progress bars will appear, indicating the remaining time for the operation to complete. Upon completion, a folder will be created in the directory where the script was executed, named after the station, containing two primary files:

        - **Attributes CSV file**, that contains metadata for each seismic event/waveform and the station itself.
        - **HDF5 waveforms file**, that stores all the waveforms as ``numpy.ndarray`` objects. The file is structured into datasets, with each dataset named according to the trace name. This enables easy identification and matching of waveforms with their respective metadata.

.. code-block:: text

    /<station_name>/
    ├── <station_name>_attributes.csv
    └── <station_name>_waveforms.hdf5

The datasets in the HDF5 file are linked to the metadata in the CSV file through the ``trace_name`` column. This allows users to easily pair waveform data with their corresponding event and station metadata.

.. warning::
    It is important not to rename these files to ensure proper integration with `processing <https://quakepro.readthedocs.io/en/latest/documentation/modules/processing.html>`_ and `visualization <https://quakepro.readthedocs.io/en/latest/documentation/modules/plot.html>`_ modules. You can safely rename the directory, but changing the filenames inside it may disrupt the functionality of other functions and methods.

For more information about subcommands and options you can use with this command, please refer to the `documentation <https://quakepro.readthedocs.io/en/latest/library/scripts/fetcher_csv.html>`_.