import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
import signal_processing

def display_data(data: np.ndarray, channel_name: str, sampling_time: float, 
                 sampling_frequency: float, dimension_unit: str, state: str) -> Figure:
    """
    Generates time-domain and frequency-domain plots for a given EEG channel.

    Args:
        data (np.ndarray): 1D array of the EEG signal.
        channel_name (str): Label of the channel (e.g., 'O1', 'Fp2').
        sampling_time (float): Total duration of the signal in seconds.
        sampling_frequency (float): Sampling rate in Hz.
        dimension_unit (str): Unit of the signal amplitude (e.g., 'uV').
        state (str): Context of the data, either "default" (raw) or "filtered".

    Returns:
        Figure: A Matplotlib Figure object containing the generated subplots.
    """
    
    # Generate precise axes
    t_axis = np.linspace(0, sampling_time, len(data))
    
    # Using NumPy's built-in fftfreq guarantees mathematical alignment with the FFT output
    f_axis = np.fft.fftshift(np.fft.fftfreq(len(data), d=1.0/sampling_frequency))

    fig, ax = plt.subplots(2, 1, figsize=(16, 8), dpi=400)

    # --- PLOT 1: TIME DOMAIN ---
    ax[0].plot(t_axis, data, color='b', linewidth=0.6)
    
    # --- PLOT 2: FREQUENCY DOMAIN (FFT) ---
    fourier_data = np.fft.fft(data) / len(data)
    fourier_data_shifted = np.fft.fftshift(fourier_data)
    ax[1].plot(f_axis, np.abs(fourier_data_shifted), color='b', linewidth=0.6)

    # --- DYNAMIC TITLES ---
    if state == "filtered":
        ax[0].set_title(f"EEG - Channel {channel_name} - Post Processing - Time Domain")
        ax[1].set_title(f"EEG - Channel {channel_name} - Post Processing - Frequency Domain")
    elif state == "default":
        ax[0].set_title(f"EEG - Channel {channel_name} - Time Domain")
        ax[1].set_title(f"EEG - Channel {channel_name} - Frequency Domain")

    # --- TIME GRAPH FORMATTING ---
    ax[0].set_xlabel("Time (s)")
    ax[0].set_ylabel(dimension_unit)
    ax[0].grid(True, linestyle="--", alpha=0.6)
    ax[0].set_xlim([0, sampling_time])

    # --- FREQUENCY GRAPH FORMATTING ---
    ax[1].set_xlabel("Frequency (Hz)")
    ax[1].grid(True, linestyle="--", alpha=0.6)
    ax[1].set_xlim([-sampling_frequency/2, sampling_frequency/2])

    fig.tight_layout()
    return fig


def display_filter(filter_coeffs: np.ndarray, filter_selected: str, sampling_frequency: float) -> Figure:
    """
    Generates the Bode plot (Magnitude and Phase response) for a given FIR filter.

    Args:
        filter_coeffs (np.ndarray): The calculated FIR filter coefficients (taps).
        filter_selected (str): The name/type of the filter for the title (e.g., 'Highpass').
        sampling_frequency (float): Sampling rate in Hz.

    Returns:
        Figure: A Matplotlib Figure object containing the Bode plot.
    """
    
    # Assuming Frequency_response is correctly defined in signal_processing to return (freq_axis, h_response)
    f_axis, h = signal_processing.Frequency_response(filter_coeffs, sampling_frequency)

    fig, ax = plt.subplots(2, 1, figsize=(16, 8), dpi=400)

    # --- PLOT 1: MAGNITUDE ---
    ax[0].set_title(f"Frequency Response of {filter_selected} FIR Filter (Magnitude)")
    
    # np.maximum prevents 'Divide by Zero' RuntimeWarnings if the filter has perfect zero attenuation
    magnitude_db = 20 * np.log10(np.maximum(np.abs(h), 1e-10))
    ax[0].plot(f_axis, magnitude_db, 'C0')
    
    ax[0].set_ylabel("Amplitude in dB", color='C0')
    ax[0].set(xlabel="Frequency in Hz")
    ax[0].grid(True)
    ax[0].axis('tight')

    # --- PLOT 2: PHASE ---
    phase = np.unwrap(np.angle(h))
    ax[1].set_title(f"Frequency Response of {filter_selected} FIR Filter (Phase)")
    ax[1].plot(f_axis, phase, 'C1')
    
    ax[1].set_ylabel('Phase [rad]', color='C1')
    ax[1].grid(True)
    ax[1].axis('tight')

    fig.tight_layout()
    return fig