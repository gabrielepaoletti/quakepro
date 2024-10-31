import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.signal import stft
from matplotlib.colors import Normalize


class _Styling:
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


class WaveformPlotter(_Styling):
    """
    A plotting class for visualizing seismic waveform data.

    Parameters
    ----------
    waveform : Waveform
        The Waveform instance containing data and metadata to be plotted.

    Attributes
    ----------
    wv : Waveform
        The waveform object containing data to be plotted.
    """

    def __init__(self, waveform: type):
        super().__init__()
        self.wv = waveform

    def _save_figure(
            self,
            save_name: str,
            save_extension: str = 'jpg',
            directory: str = './quakepro_figures'
        ) -> None:
        """
        Save the current matplotlib figure to a specified directory.

        Parameters
        ----------
        save_name : str
            The base name for the saved figure file.
        save_extension : str, optional
            The file extension for the saved figure, by default 'jpg'.
        directory : str, optional
            Directory where the figure will be saved, by default './quakepro_figures'.
        """
        os.makedirs(directory, exist_ok=True)
        fig_name = os.path.join(directory, f'{save_name}.{save_extension}')
        plt.savefig(fig_name, dpi=300, bbox_inches='tight')

    def plot_waveform(
            self,
            save_figure: bool = False,
            save_extension: str = 'jpg'
        ) -> None:
        """
        Plot the waveform data and optionally save the figure.

        Parameters
        ----------
        save_figure : bool, optional
            If True, saves the plot as a file, by default False.
        save_extension : str, optional
            The file extension for the saved figure, by default 'jpg'.
        """
        _, axs = plt.subplots(
            len(self.wv.data), 1, figsize=(12, 2 * len(self.wv.data)),
            sharex=True, sharey=True
        )

        for cha, sig in enumerate(self.wv.data):
            axs[cha].plot(sig, c='k', lw=0.75, label=f'CH{cha + 1}')
            axs[cha].set_ylabel('Amplitude')
            axs[cha].set_xlim(0, len(sig))
            axs[cha].legend(loc='upper right')
            axs[cha].grid(True, axis='x')

        axs[0].set_title(f'{self.wv.trace_name}')
        axs[-1].set_xlabel('Samples [#]')
        
        plt.tight_layout()
        
        if save_figure:
            self._save_figure(f'{self.wv.trace_name}', save_extension)

        plt.show()
    
    def plot_spectra(
            self,
            log_scale: bool = True,
            plot_waveform: bool = True,
            save_figure: bool = False,
            save_extension: str = 'jpg'
        ) -> None:
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
        for cha, sig in enumerate(self.wv.data):
            ft = np.fft.fft(sig)
            freq = np.fft.fftfreq(sig.size, d=1 / self.wv.sampling_rate_hz)
            N = sig.size
            ft = ft / N
            half_point = N // 2
            freq = freq[:half_point]
            amplitude_spectrum = np.abs(ft)[:half_point] * 2

            if plot_waveform:
                _, axs = plt.subplots(
                    2, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [1, 3]}
                )
            else:
                _, axs = plt.subplots(1, 1, figsize=(10, 6))
                axs = [axs]

            axs[0].set_title(f'{self.wv.trace_name}')
            if plot_waveform:
                axs[0].plot(sig, linewidth=0.75, color='k', label=f'CH{cha + 1}')
                axs[0].set_xlabel('Samples [#]')
                axs[0].set_ylabel('Amplitude')
                axs[0].set_xlim(0, len(sig))
                axs[0].grid(True, axis='x')
                axs[0].legend(loc='upper right')

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
                self._save_figure(f'spectra_{self.wv.trace_name}', save_extension)
            plt.show()
    
    def plot_spectrogram(
            self,
            nperseg: int = 128,
            noverlap: int = None,
            log_scale: bool = False,
            zero_padding_factor: int = 8,
            plot_waveform: bool = True,
            colorbar: bool = False,
            cmap: str = 'jet',
            save_figure: bool = False,
            save_extension: str = 'jpg'
        ) -> None:
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
        save_extension : str, optional
            The file extension for the saved figure, by default 'jpg'.
        """
        for cha, signal in enumerate(self.wv.data):
            signal -= np.mean(signal)
            noverlap = noverlap or int(nperseg * 0.75)

            nfft = nperseg * zero_padding_factor
            frequencies, times, Zxx = stft(
                signal, fs=self.wv.sampling_rate_hz, window='hann',
                nperseg=nperseg, noverlap=noverlap, nfft=nfft
            )
            spectrogram = np.abs(Zxx)**2

            if log_scale:
                spectrogram = 10 * np.log10(spectrogram)
            else:
                spectrogram = np.sqrt(spectrogram) * 2

            fig = plt.figure(figsize=(10, 7))
            gs = gridspec.GridSpec(
                2, 2, width_ratios=[25, 1], height_ratios=[1, 3],
                wspace=0.05, hspace=0.15
            )
            
            if plot_waveform:
                ax1 = fig.add_subplot(gs[0, 0])
                time = np.arange(signal.size) / self.wv.sampling_rate_hz
                ax1.plot(time, signal, color='k', linewidth=0.75, label=f'CH{cha + 1}')
                ax1.set_title(f'{self.wv.trace_name}')
                ax1.set_ylabel('Amplitude')
                ax1.grid(True, axis='x')
                ax1.tick_params(axis='x', labelbottom=False)
                ax1.set_xlim(0, signal.size / self.wv.sampling_rate_hz)
                ax1.legend(loc='upper right')

            ax2 = fig.add_subplot(gs[1, 0], sharex=ax1 if plot_waveform else None)
            pcm = ax2.pcolormesh(
                times, frequencies, spectrogram, shading='gouraud',
                cmap=cmap, norm=Normalize(vmin=np.min(spectrogram), vmax=np.max(spectrogram))
            )
            if not plot_waveform:
                ax2.set_title(f'{self.wv.trace_name}')
            ax2.set_ylabel('Frequency [Hz]')
            ax2.set_xlabel('Time [s]')
        
            if colorbar:
                cax = fig.add_subplot(gs[1, -1])
                cbar = plt.colorbar(pcm, cax=cax)
                cbar.set_label(
                    'Power spectral density [dB]' if log_scale else 'Amplitude'
                )

            plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
            if save_figure:
                self._save_figure(f'spectrogram_{self.wv.trace_name}', save_extension)

            plt.show()