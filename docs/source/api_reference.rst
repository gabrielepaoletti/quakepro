API Reference
=============

.. toctree::
   :maxdepth: 1
   :hidden:
   :caption: Components
   
   library/components/waveform
   library/components/dataset

.. toctree::
   :maxdepth: 1
   :hidden:
   :caption: Executable scripts
   
   library/scripts/fetcher_csv

This reference manual offers detailed explanations of the functions, modules, and objects contained within QUAKEPRO, outlining their purposes and functionalities. To learn how to apply QUAKEPRO, please refer to the `tutorial page <https://quakepro.readthedocs.io/en/latest/user_guide/tutorials.html>`_.

Core
----
The primary interface for interacting with seismic waveform data, providing essential functions for data import and basic management.

.. card:: :material-outlined:`hub;1.7em` Core
   :link: library/core
   :link-type: doc

   Provides essential functions for importing and organizing seismic datasets.

Components
----------
Defines the core objects of the library, encapsulating both individual seismic waveforms and collections of waveforms. These objects are foundational for handling and analyzing seismic data in a structured and efficient way.

.. card:: :material-outlined:`rss_feed;1.7em` Waveform
   :link: library/components/waveform
   :link-type: doc

   Encapsulates a seismic waveform, including data and relevant metadata.

.. card:: :material-outlined:`dataset;1.7em` Dataset
   :link: library/components/dataset
   :link-type: doc

   Provides batch management and processing capabilities for waveform collections.

Executable scripts
------------------

Include command-line interfaces (CLI) designed for speed up tasks, offering an efficient and user-friendly approach to handle large datasets and prepare them for subsequent analysis.

.. card:: :material-outlined:`download;1.7em` Fetchers
   :link: library/scripts/fetchers
   :link-type: doc

   Scripts for downloading waveforms, each offering a unique method of retrieval.