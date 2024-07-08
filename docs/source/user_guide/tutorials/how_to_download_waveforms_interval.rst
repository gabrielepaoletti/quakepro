How to download waveforms for custom time intervals
======================================================

In this tutorial, you will learn how to efficiently download seismic waveforms using QUAKEPRO for custom time intervals. This guide is designed to assist you in setting up the parameters for time intervals, waveform lengths, and sampling frequencies to seamlessly retrieve the necessary waveform data.

Waveform download
-----------------

You can download the waveforms by opening the command prompt and running the download script (ensure QUAKEPRO is `installed <https://quakepro.readthedocs.io/en/latest/user_guide/installation.html>`_ on your device):

.. code-block:: bash

    qpf-csv -p INGV -n IV -s MMO1 -c EH* -l * --start_time 2016-01-01 --end_time 2017-01-01 --trace_len 30s --interval 12H

.. note::
    In this command, wildcards are used to specify multiple options conveniently. For example, ``EH*`` indicates that all channels starting with ``EH`` should be downloaded. This flexibility allows you to customize the command to suit your specific needs.

.. note::
    For the parameters --trace_len and --interval, you must use Pandas time strings. For more information, refer to the `https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#period-aliases>`_.

This command will download 30-second three-channel waveforms every 12 hours from the MMO1 seismic station, covering the period from January 1, 2016, to January 1, 2017.

When the software is running, progress bars will appear, indicating the remaining time for the operation to complete. Upon completion, a folder will be created in the directory where the script was executed, named after the station, containing two primary files:

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

For more information about subcommands and options you can use with this command, please refer to the `documentation <https://quakepro.readthedocs.io/en/latest/library/scripts/fetcher_csv.html>`_.