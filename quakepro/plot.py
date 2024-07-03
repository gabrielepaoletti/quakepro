"""
@author: Gabriele Paoletti
@e-mail: gabriele.paoletti@uniroma1.it
"""

# --------------------------------------------------------------------------------------------------------
# IMPORTING REQUIRED MODULES
# --------------------------------------------------------------------------------------------------------

import os
import h5py
import random

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from scipy.signal import stft
from matplotlib.colors import Normalize

from typing import Union

# --------------------------------------------------------------------------------------------------------
# DEFINING CLASSES AND METHODS
# --------------------------------------------------------------------------------------------------------

class _PlotConfig:
    def __init__(self) -> None:
        """
        Initializes the PlotConfig class with an custom style.

        Returns
        -------
        None
        """
        self._set_style()

    def _set_style(self) -> None:
        """
        Applies the default style with an option to override with custom style.

        Returns
        -------
        None        
        """
        plt.rcParams.update({
            'axes.spines.top': False,
            'axes.spines.right': False,
            'axes.titlesize': 16,
            'axes.titleweight': 'bold',
            'axes.labelsize': 14,
            'legend.fontsize': 12,
            'legend.frameon': False,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10,
            'grid.alpha': 0.25,
            'grid.linestyle': ':'
        })

    def save_figure(self, save_name: str, save_extension: str='jpg', directory: str='./quakepro_figures') -> None:
        """
        Saves the given figure to a file with the specified name, extension, and directory.

        Parameters
        ----------
        save_name : str, optional
            The base name used for saving figures when `save_figure` is True. It serves as the prefix for file names.

        save_extension : str, optional
            The file extension to use when saving figures, such as 'jpg', 'png', etc... The default extension is 'jpg'.

        directory : str, optional
            The directory where the figure will be saved (default is './swf_figures').

        Returns
        -------
        None
        """
        os.makedirs(directory, exist_ok=True)
        fig_name = os.path.join(directory, f'{save_name}.{save_extension}')
        plt.savefig(fig_name, dpi=300, bbox_inches='tight')

class Plotter(_PlotConfig):
    def __init__(self, waveforms: h5py.File, attributes: pd.DataFrame) -> None:
        """
        Initialize the Plotter instance with waveform data and attributes.

        Parameters
        ----------
        waveforms : h5py.File
            An HDF5 file object containing waveform data.
        
        attributes : pd.DataFrame
            A pandas DataFrame containing attributes related to the waveforms.

        Returns
        -------
        None
        """
        super().__init__()
        self.wavs = waveforms
        self.attr = attributes

    def plot_waveform(self, slice_obj: Union[slice, int, str]='random', save_figure: bool=False, save_name: str='waveform', save_extension: str='jpg') -> None:
        """
        Plot the waveform of a selected event in the HDF5 file.

        Parameters
        ----------
        slice_obj : Union[slice, int, str], optional
            The slice object or 'random' to select a waveform. Default is 'random'.

        save_figure : bool, optional
            If True, save the figure. Default is False.

        save_name : str, optional
            The name to save the figure. Default is 'fourier_transform'.

        save_extension : str, optional
            The file extension to save the figure. Default is 'jpg'.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If `slice_obj` is not an integer, a slice object, or the string 'random'.
        """
        if slice_obj == 'random':
            index = random.randint(0, len(self.attr['trace_name']) - 1)
            trace_names = [self.attr['trace_name'].iloc[index]]
        elif isinstance(slice_obj, int):
            trace_names = [self.attr['trace_name'].iloc[slice_obj]]
        elif isinstance(slice_obj, slice):
            trace_names = self.attr['trace_name'].iloc[slice_obj]
        else:
            raise ValueError("slice_obj must be 'random' or a slice object")
        
        for _, trace_name in enumerate(trace_names):
            fig, axs = plt.subplots(3, 1, figsize=(10, 5), sharex=True, sharey=True)
            signals = self.wavs[trace_name][:]

            for ch_idx, signal in enumerate(signals):
                axs[ch_idx].plot(signal, c='k', lw=0.75, label=f'CH{ch_idx + 1}')
                axs[ch_idx].set_ylabel('Amplitude')
                axs[ch_idx].set_xlim(0, len(signal))
                axs[ch_idx].legend(loc='upper right')
                axs[ch_idx].grid(True, axis='x')
            
                axs[0].set_title(f'Event ID-{self.attr[self.attr.trace_name == trace_name].src_id.item()}')
                axs[-1].set_xlabel('Samples [#]')
                
            plt.tight_layout()
            if save_figure:
                self.save_figure(f'{save_name}_{self.attr[self.attr.trace_name == trace_name].src_id.item()}', save_extension)

            plt.show()

    def plot_fourier_transform(self, slice_obj: Union[slice, int, str]='random', log_scale: bool=True, plot_waveform: bool=True, save_figure: bool=False, save_name: str='fourier_transform', save_extension: str='jpg') -> None:
        """
        Plot the fourier transform of a selected waveform in the HDF5 file.

        Parameters
        ----------
        slice_obj : Union[slice, int, str], optional
            The slice object or 'random' to select a waveform. Default is 'random'.

        log_scale : bool, optional
            If True, plot on a logarithmic scale. Default is True.

        plot_waveform : bool, optional
            If True, plot the waveform along with the Fourier Transform. Default is True.

        save_figure : bool, optional
            If True, save the figure. Default is False.

        save_name : str, optional
            The name to save the figure. Default is 'fourier_transform'.

        save_extension : str, optional
            The file extension to save the figure. Default is 'jpg'.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If `slice_obj` is not an integer, a slice object, or the string 'random'.
        """
        if slice_obj == 'random':
            index = random.randint(0, len(self.attr['trace_name']) - 1)
            trace_names = [self.attr['trace_name'].iloc[index]]
        elif isinstance(slice_obj, int):
            trace_names = [self.attr['trace_name'].iloc[slice_obj]]
        elif isinstance(slice_obj, slice):
            trace_names = self.attr['trace_name'].iloc[slice_obj]
        else:
            raise ValueError("slice_obj must be 'random' or a slice object")
        
        for _, trace_name in enumerate(trace_names):
            signals = self.wavs[trace_name][:]
            
            for ch_idx, signal in enumerate(signals):
                # Perform Fourier Transform
                ft = np.fft.fft(signal)
                freq = np.fft.fftfreq(signal.size, d=1/self.attr[self.attr.trace_name == trace_name].rec_sampling_rate_hz.item())
                N = signal.size
                ft = ft / N  # Normalize the amplitudes
                half_point = N // 2
                freq = freq[:half_point]
                amplitude_spectrum = np.abs(ft)[:half_point] * 2  # Multiply by 2 to account for symmetrical nature of FFT output

                # Plotting
                if plot_waveform:
                    fig, axs = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [1, 3]})
                else:
                    fig, axs = plt.subplots(1, 1, figsize=(10, 6))
                    axs = [axs]  # Make it iterable for the upcoming loop

                # Plot the waveform
                axs[0].set_title(f'Event ID-{self.attr[self.attr.trace_name == trace_name].src_id.item()}')
                if plot_waveform:
                    axs[0].plot(signal, linewidth=0.75, color='k', label=f'CH{ch_idx + 1}')
                    axs[0].set_xlabel('Samples [#]')
                    axs[0].set_ylabel('Amplitude')
                    axs[0].set_xlim(0, len(signal))
                    axs[0].grid(True, axis='x',)
                    axs[0].legend(loc='upper right')

                # Plot the Fourier Transform
                ax = axs[-1]

                if log_scale:
                    ax.loglog(freq, amplitude_spectrum, color='black', linewidth=0.75)
                else:
                    ax.plot(freq, amplitude_spectrum, color='black', linewidth=0.75)

                ax.set_xlabel('Frequency [Hz]')
                ax.set_ylabel('Amplitude')
                ax.grid(True, which='both')

                plt.tight_layout()
                if save_figure:
                    self.save_figure(f'{save_name}_{self.attr[self.attr.trace_name == trace_name].src_id.item()}', save_extension)
                plt.show()
    
    def plot_spectrogram(self, slice_obj: Union[slice, int, str] = 'random', nperseg: int = 128, noverlap: int = None, log_scale: bool = False, zero_padding_factor: int = 8, plot_waveform: bool = True, colorbar: bool = False, cmap: str = 'jet', save_figure: bool = False, save_name: str = 'spectrogram', save_extension: str = 'jpg') -> None:
        """
        Plot the spectrogram of a selected waveform in the HDF5 file.

        Parameters
        ----------
        slice_obj : Union[slice, int, str], optional
            The slice object or 'random' to select a waveform. Default is 'random'.

        nperseg : int, optional
            Length of each segment for STFT. Default is 128.

        noverlap : int, optional
            Number of points to overlap between segments. Default is None.

        log_scale : bool, optional
            If True, plot on a logarithmic scale. Default is False.

        zero_padding_factor : int, optional
            Factor by which to zero-pad the FFT. Default is 8.

        plot_waveform : bool, optional
            If True, plot the waveform along with the spectrogram. Default is True.

        colorbar : bool, optional
            If True, add a colorbar to the spectrogram. Default is False.

        cmap : str, optional
            Colormap to use for the spectrogram. Default is 'jet'.

        save_figure : bool, optional
            If True, save the figure. Default is False.

        save_name : str, optional
            The name to save the figure. Default is 'spectrogram'.

        save_extension : str, optional
            The file extension to save the figure. Default is 'jpg'.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If `slice_obj` is not an integer, a slice object, or the string 'random'.
        """
        if slice_obj == 'random':
            index = random.randint(0, len(self.attr['trace_name']) - 1)
            trace_names = [self.attr['trace_name'].iloc[index]]
        elif isinstance(slice_obj, int):
            trace_names = [self.attr['trace_name'].iloc[slice_obj]]
        elif isinstance(slice_obj, slice):
            trace_names = self.attr['trace_name'].iloc[slice_obj]
        else:
            raise ValueError("slice_obj must be 'random' or a slice object")

        for _, trace_name in enumerate(trace_names):
            signals = self.wavs[trace_name][:]
            
            for ch_index, signal in enumerate(signals):

                signal -= np.mean(signal)
                if noverlap is None:
                    noverlap = int(nperseg * 0.75)

                nfft = nperseg * zero_padding_factor
                sampling_rate = self.attr[self.attr.trace_name == trace_name].rec_sampling_rate_hz.item()
                frequencies, times, Zxx = stft(signal, fs=sampling_rate, window='hann', nperseg=nperseg, noverlap=noverlap, nfft=nfft)
                spectrogram = np.abs(Zxx)**2

                if log_scale:
                    spectrogram = 10 * np.log10(spectrogram)
                else:
                    spectrogram = np.sqrt(spectrogram) * 2

                fig = plt.figure(figsize=(10, 7))
                gs = gridspec.GridSpec(2, 2, width_ratios=[25, 1], height_ratios=[1, 3], wspace=0.05, hspace=0.15)
                
                if plot_waveform:
                    ax1 = fig.add_subplot(gs[0, 0])
                    time = np.arange(signal.size) / sampling_rate
                    ax1.plot(time, signal, color='k', linewidth=0.75, label=f'CH{ch_index + 1}')
                    ax1.set_title(f'Event ID-{self.attr[self.attr.trace_name == trace_name].src_id.item()}')
                    ax1.set_ylabel('Amplitude')
                    ax1.grid(True, axis='x')
                    ax1.tick_params(axis='x', labelbottom=False)
                    ax1.set_xlim(0, signal.size / sampling_rate)
                    ax1.legend(loc='upper right')

                ax2 = fig.add_subplot(gs[1, 0], sharex=ax1 if plot_waveform else None)
                pcm = ax2.pcolormesh(times, frequencies, spectrogram, shading='gouraud', cmap=cmap, norm=Normalize(vmin=np.min(spectrogram), vmax=np.max(spectrogram)))
                ax2.set_title(f'Event ID-{self.attr[self.attr.trace_name == trace_name].src_id.item()}') if not plot_waveform else None
                ax2.set_ylabel('Frequency [Hz]')
                ax2.set_xlabel('Time [s]')
            
                if colorbar:
                    cax = fig.add_subplot(gs[1, -1])
                    cbar = plt.colorbar(pcm, cax=cax)
                    cbar.set_label('Power spectral density [dB]' if log_scale else 'Amplitude')

                # Adjust layout manually instead of tight_layout
                plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
                if save_figure:
                    self.save_figure(f'{save_name}_{self.attr[self.attr.trace_name == trace_name].src_id.item()}', save_extension)

                plt.show()