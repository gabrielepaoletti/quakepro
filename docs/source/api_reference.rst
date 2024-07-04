API Reference
=============

.. toctree::
   :maxdepth: 1
   :hidden:
   :caption: Modules
   
   documentation/modules/processing
   documentation/modules/plot

.. toctree::
   :maxdepth: 1
   :hidden:
   :caption: Executable scripts
   
   documentation/scripts/fetcher_csv

This reference manual offers detailed explanations of the functions, modules, and objects contained within QUAKEPRO, outlining their purposes and functionalities. To learn how to apply QUAKEPRO, please refer to the `tutorial page <https://quakepro.readthedocs.io/en/latest/user_guide/tutorials.html>`_.

Modules
-------
Provide a comprehensive set of Python tools primarily focused on signal processing and visualization, facilitating in-depth analysis and interpretation of seismic data through customizable and efficient code implementations.


.. card:: :material-outlined:`earthquake;1.7em` Processing
   :link: documentation/modules/processing
   :link-type: doc

   Process waveform data to tailor and refine seismic signal characteristics for detailed analysis.

.. card:: :material-outlined:`image;1.7em` Visualization
   :link: documentation/modules/plot
   :link-type: doc

   Offer tools for the effective visualization of seismic waveforms and their features.

Executable scripts
------------------

Include command-line interfaces (CLI) designed for the streamlined downloading of seismic waveforms and pre-processing tasks, offering an efficient and user-friendly approach to handle large datasets and prepare them for subsequent analysis.

.. card:: :material-outlined:`download;1.7em` QPF-CSV
   :link: documentation/scripts/fetcher_csv
   :link-type: doc

   Fetch seismic waveforms from pre-built CSV earthquake catalogs.