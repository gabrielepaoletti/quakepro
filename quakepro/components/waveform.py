import numpy as np
import pandas as pd

from quakepro.internal.decorators import sync_signature
from quakepro.components.ops.plotting import WaveformPlotter
from quakepro.components.ops.processing import WaveformProcessor


class Waveform:
    """
    A class representing a single seismic waveform and its associated metadata.

    Parameters
    ----------
    data : np.ndarray
        Array containing the seismic waveform data.
    attrs : pd.Series
        Series containing metadata attributes for the waveform.
    
    Attributes
    ----------
    data : np.ndarray
        The seismic waveform data.
    _plotter : WaveformPlotter
        An instance of WaveformPlotter for visualizing the waveform.
    """

    def __init__(self, data: np.ndarray, attrs: pd.Series, trans: str = None):
        self.data = data

        self._attrs = attrs
        self._plotter = WaveformPlotter(self)
        self._processor = WaveformProcessor(self)

        for column_name, column_value in attrs.items():
            setattr(self, column_name, column_value)

    @sync_signature('_processor', 'filter', WaveformProcessor)
    def filter(self, **kwargs) -> None:
        """
        Apply a Butterworth filter to the waveform data.

        Parameters
        ----------
        filter_type : str
            Type of filter to apply ('lowpass', 'highpass', 'bandpass', 'bandstop').
        cutoff : int or list
            Cutoff frequency/frequencies for the filter. If a list, specifies 
            the range for bandpass or bandstop filters.
        order : int, optional
            The order of the filter, by default 5.
        zero_phase : bool, optional
            If True, applies a zero-phase filter using sosfiltfilt for no phase shift, 
            by default True.

        Returns
        -------
        Waveform
            A new Waveform instance with the filtered data.
        """
        self._processor.filter(**kwargs)

    @sync_signature('_processor', 'taper', WaveformProcessor)
    def taper(self, **kwargs) -> None:
        """
        Apply a tapering window to the waveform data.

        Parameters
        ----------
        window_type : str
            Type of window to apply (e.g., 'hann', 'hamming').
        *args
            Additional arguments to define the shape or properties of the window.

        Returns
        -------
        Waveform
            A new Waveform instance with the tapered data.
        """
        self._processor.taper(**kwargs)

    @sync_signature('_plotter', 'plot_waveform', WaveformPlotter)
    def plot(self, **kwargs) -> None:
        """
        Plot the waveform data and optionally save the figure.

        Parameters
        ----------
        save_figure : bool, optional
            If True, saves the plot as a file, by default False.
        save_extension : str, optional
            The file extension for the saved figure, by default 'jpg'.
        """
        self._plotter.plot_waveform(**kwargs)

    @sync_signature('_plotter', 'plot_spectra', WaveformPlotter)
    def plot_spectra(self, **kwargs) -> None:
        """
        Plot the amplitude spectrum of each waveform channel.

        Parameters
        ----------
        log_scale : bool, optional
            If True, plots on a log-log scale, by default True.
        plot_waveform : bool, optional
            If True, includes the original waveform plot above the spectrum,
            by default True.
        save_figure : bool, optional
            If True, saves the plot as a file, by default False.
        save_extension : str, optional
            The file extension for the saved figure, by default 'jpg'.
        """
        self._plotter.plot_spectra(**kwargs)

    @sync_signature('_plotter', 'plot_spectrogram', WaveformPlotter)
    def plot_spectrogram(self, **kwargs) -> None:
        """
        Plot the spectrogram for each channel of the waveform.

        Parameters
        ----------
        nperseg : int, optional
            Length of each segment for STFT, by default 128.
        noverlap : int, optional
            Number of points to overlap between segments, by default None.
        log_scale : bool, optional
            If True, applies logarithmic scaling to the spectrogram, by default False.
        zero_padding_factor : int, optional
            Factor for zero-padding, affecting the resolution of the FFT, by default 8.
        plot_waveform : bool, optional
            If True, includes the waveform plot above the spectrogram, by default True.
        colorbar : bool, optional
            If True, includes a colorbar, by default False.
        cmap : str, optional
            Colormap for the spectrogram, by default 'jet'.
        save_figure : bool, optional
            If True, saves the plot as a file, by default False.
        save_name : str, optional
            The base name for the saved figure file, by default 'spectrogram'.
        save_extension : str, optional
            The file extension for the saved figure, by default 'jpg'.
        """
        self._plotter.plot_spectrogram(**kwargs)

    def __repr__(self) -> str:
        """
        Return a string representation of the Waveform instance.

        Returns
        -------
        str
            A string showing the trace name of the waveform.
        """
        return f'Waveform({self.trace_name})'

    def __str__(self) -> str:
        """
        Return a detailed string representation of the Waveform instance, 
        excluding the waveform data.

        Returns
        -------
        str
            A string with the waveform attributes and metadata.
        """
        parts = [f"{self.__class__.__name__}("]
        for key, value in self.__dict__.items():
            if key.startswith('_') or key in ['data', 'instance']:
                continue
            elif isinstance(value, str) and value.startswith("<") and value.endswith(">"):
                parts.append(f"    {key}={value}")
            else:
                parts.append(f"    {key}={repr(value)}")
        parts.append(")")
        return "\n".join(parts)