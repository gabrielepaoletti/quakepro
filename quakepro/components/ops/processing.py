import numpy as np
from scipy.signal import butter, sosfilt, sosfiltfilt, get_window


class WaveformProcessor:
    """
    A processing class for applying filtering and tapering operations to 
    seismic waveform data.

    Parameters
    ----------
    waveform : Waveform
        The Waveform instance containing data to be processed.

    Attributes
    ----------
    wv : Waveform
        The waveform object containing data and metadata for processing.
    """

    def __init__(self, waveform: type):
        self.wv = waveform

    def filter(
            self,
            filter_type: str,
            cutoff: int | list,
            order: int = 5,
            zero_phase: bool = True
        ) -> 'Waveform':
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
        nyq = 0.5 * self.wv.sampling_rate_hz
        normal_cutoff = (
            [c / nyq for c in cutoff] if isinstance(cutoff, list) else cutoff / nyq
        )
        sos = butter(order, normal_cutoff, btype=filter_type, output='sos')

        filtered_signals = np.zeros_like(self.wv.data)
        for cha, signal in enumerate(self.wv.data):
            if zero_phase:
                filtered_signals[cha] = sosfiltfilt(sos, signal)
            else:
                filtered_signals[cha] = sosfilt(sos, signal)

        from quakepro.components.waveform import Waveform
        return Waveform(
            data=filtered_signals,
            attrs=self.wv._attrs,
        )

    def taper(
            self, 
            window_type: str,
            *args
        ) -> 'Waveform':
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
        tapered_signals = np.zeros_like(self.wv.data)
        for cha, signal in enumerate(self.wv.data):
            window = (
                get_window((window_type, *args), len(signal))
                if args else get_window(window_type, len(signal))
            )
            tapered_signals[cha] = signal * window

        from quakepro.components.waveform import Waveform
        return Waveform(
            data=tapered_signals,
            attrs=self.wv._attrs,
        )
