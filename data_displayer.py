import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path
from matplotlib.figure import Figure
import numpy as np
import signal_processing

"""
This module provides functions to visualize EEG data,
filter responses, 
independent components, 
and scalp maps.
"""

def display_data(data: np.ndarray, channel_name: str, sampling_time: float, 
                 sampling_frequency: float, dimension_unit: str) -> Figure:
    """
    Generates time-domain and frequency-domain plots for a given EEG channel.

    Args:
        data (np.ndarray): 1D array of the EEG signal.
        channel_name (str): Label of the channel (e.g., 'O1', 'Fp2').
        sampling_time (float): Total duration of the signal in seconds.
        sampling_frequency (float): Sampling rate in Hz.
        dimension_unit (str): Unit of the signal amplitude (e.g., 'uV').

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
    data_centered = data - np.mean(data)  # Center the signal to remove DC offset
    fourier_data = np.fft.fft(data_centered) / len(data)
    fourier_data_shifted = np.fft.fftshift(fourier_data)
    ax[1].plot(f_axis, np.abs(fourier_data_shifted), color='b', linewidth=0.6)

    # --- TITLES ---
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


def compare_filter(Fir_win: np.ndarray, Fir_eqr: np.ndarray, Fir_lsq: np.ndarray, filter_selected: str, sampling_frequency :float) -> Figure:

    """
    Allows to compare the three methods proposed (Window, Equiripple, Least Squares) to help the user decide the filter features needed.
    To achieve a reasonable comparison, all filters will be designed using the same parameters through the streamlit interface by the user /
    in the Jupyter Notebook by the author.

    Args:
        Fir_win, Fir_eqr, Fir_lsq (np.ndarray): The calculated FIR filters coefficients (taps).
        filter_selected (str): The name/type of the filter for the title (e.g., 'Highpass').
        sampling_frequency (float): Sampling rate in Hz.

    Returns:
        Figure: A Matplotlib Figure object containing the Bode plot of the three filters.

    """

    fig, ax = plt.subplots(2, 3, figsize=(16,8), dpi=400)

    f_axis, h_window = signal_processing.Frequency_response(Fir_win, sampling_frequency)
    h_equiripple = signal_processing.Frequency_response(Fir_eqr, sampling_frequency)[1]
    h_leastsquares = signal_processing.Frequency_response(Fir_lsq, sampling_frequency)[1]

    # --- PLOT [0,0]: MAGNITUDE WINDOW---
    ax[0,0].set_title(f"{filter_selected} Window FIR Filter (Magnitude)")
    # np.maximum prevents 'Divide by Zero' RuntimeWarnings if the filter has perfect zero attenuation
    magnitude_db_win = 20 * np.log10(np.maximum(np.abs(h_window), 1e-10))
    ax[0,0].plot(f_axis, magnitude_db_win, 'C0')
        
    ax[0,0].set_ylabel("Amplitude in dB", color='C0')
    ax[0,0].set(xlabel="Frequency in Hz")
    ax[0,0].grid(True)
    ax[0,0].axis('tight')
    
    # --- PLOT [1,0]: PHASE WINDOW---
    phase_win = np.unwrap(np.angle(h_window))
    ax[1,0].set_title(f"{filter_selected} Window FIR Filter (Phase)")
    ax[1,0].plot(f_axis, phase_win, 'C1')
        
    ax[1,0].set_ylabel('Phase [rad]', color='C1')
    ax[1,0].set(xlabel="Frequency in Hz")
    ax[1,0].grid(True)
    ax[1,0].axis('tight')

    # --- PLOT [0,1]: MAGNITUDE EQUIRIPPLE---
    ax[0,1].set_title(f"{filter_selected} Equiripple FIR Filter (Magnitude)")
    # np.maximum prevents 'Divide by Zero' RuntimeWarnings if the filter has perfect zero attenuation
    magnitude_db_eqr = 20 * np.log10(np.maximum(np.abs(h_equiripple), 1e-10))
    ax[0,1].plot(f_axis, magnitude_db_eqr, 'C0')
        
    ax[0,1].set_ylabel("Amplitude in dB", color='C0')
    ax[0,1].set(xlabel="Frequency in Hz")
    ax[0,1].grid(True)
    ax[0,1].axis('tight')
    
    # --- PLOT [1,1]: PHASE EQUIRIPPLE---
    phase_eqr = np.unwrap(np.angle(h_equiripple))
    ax[1,1].set_title(f"{filter_selected} Equiripple FIR Filter (Phase)")
    ax[1,1].plot(f_axis, phase_eqr, 'C1')
        
    ax[1,1].set_ylabel('Phase [rad]', color='C1')
    ax[1,1].set(xlabel="Frequency in Hz")
    ax[1,1].grid(True)
    ax[1,1].axis('tight')

    # --- PLOT [0,2]: MAGNITUDE L SQUARES---
    ax[0,2].set_title(f"{filter_selected} Least Squares FIR Filter (Magnitude)")
    # np.maximum prevents 'Divide by Zero' RuntimeWarnings if the filter has perfect zero attenuation
    magnitude_db_lsq = 20 * np.log10(np.maximum(np.abs(h_leastsquares), 1e-10))
    ax[0,2].plot(f_axis, magnitude_db_lsq, 'C0')
        
    ax[0,2].set_ylabel("Amplitude in dB", color='C0')
    ax[0,2].set(xlabel="Frequency in Hz")
    ax[0,2].grid(True)
    ax[0,2].axis('tight')
    
    # --- PLOT [1,2]: PHASE L SQUARES---
    phase_lsq = np.unwrap(np.angle(h_leastsquares))
    ax[1,2].set_title(f"{filter_selected} Least Squares FIR Filter (Phase)")
    ax[1,2].plot(f_axis, phase_lsq, 'C1')
        
    ax[1,2].set_ylabel('Phase [rad]', color='C1')
    ax[1,2].set(xlabel="Frequency in Hz")
    ax[1,2].grid(True)
    ax[1,2].axis('tight')

    fig.tight_layout()
    
    return fig

def displayer(data: np.ndarray, time_start: float, time_width: float, channel_names: list, sampling_frequency: float, dimension_unit: str) -> Figure:
    """
    Displays the EEG data for all channels in a grid layout, 
    showing both time-domain and frequency-domain plots for each channel.
    """
    start_index = int(time_start * sampling_frequency)
    end_index = int((time_start + time_width) * sampling_frequency)

    data_window = data[:, start_index:end_index]
    
    # Calculate the exact number of samples in this window
    n_samples = data_window.shape[1] 

    # Generate precise axes
    t_axis = np.linspace(time_start, time_start + time_width, n_samples)

    f_axis = np.fft.fftshift(np.fft.fftfreq(n_samples, d=1.0/sampling_frequency)) 

    # Define the lobes based on channel names
    lobes = {
        "Frontal": [i for i, name in enumerate(channel_names) if name.upper().startswith(('F', 'AF', 'FP'))],
        "Central": [i for i, name in enumerate(channel_names) if name.upper().startswith('C')],
        "Temporal": [i for i, name in enumerate(channel_names) if name.upper().startswith('T')],
        "Parietal": [i for i, name in enumerate(channel_names) if name.upper().startswith('P')],
        "Occipital": [i for i, name in enumerate(channel_names) if name.upper().startswith(('O','I'))]
    }

    # Filter out empty lobes to avoid plotting blank graphs
    lobes = {k: v for k, v in lobes.items() if len(v) > 0}
    n_lobes = len(lobes)

    fig, ax = plt.subplots(n_lobes, 2, figsize=(14, 3.5*n_lobes), dpi=150)
    
    # Safety check: if only 1 lobe is found, ax is not a 2D array, which causes a crash in the loop
    if n_lobes == 1:
        ax = np.expand_dims(ax, axis=0)

    for idx, (lobe_name, channels) in enumerate(lobes.items()):
        
        # --- PLOT 1: TIME DOMAIN (Butterfly) ---
        for ch in channels:

            ax[idx, 0].plot(t_axis, data_window[ch, :], linewidth=0.5, alpha=0.7)
            
        ax[idx, 0].set_title(f"Time Domain - {lobe_name} Lobe")
        ax[idx, 0].set_xlabel("Time (s)")
        ax[idx, 0].set_ylabel(dimension_unit)
        ax[idx, 0].grid(True, linestyle="--", alpha=0.6)
        ax[idx, 0].set_xlim([time_start, time_start + time_width])

        # --- PLOT 2: FREQUENCY DOMAIN (FFT) ---
        for ch in channels:

            data_centered = data_window[ch, :] - np.mean(data_window[ch, :])  # Center the signal to remove DC offset

            fourier_data = np.fft.fft(data_centered) / n_samples  
            fourier_data_shifted = np.fft.fftshift(fourier_data)
            ax[idx, 1].plot(f_axis, np.abs(fourier_data_shifted), linewidth=0.5, alpha=0.7)
            
        ax[idx, 1].set_title(f"Frequency Domain - {lobe_name} Lobe")
        ax[idx, 1].set_xlabel("Frequency (Hz)")
        ax[idx, 1].grid(True, linestyle="--", alpha=0.6)
        
        # Only show positive frequencies up to Nyquist for a cleaner look
        ax[idx, 1].set_xlim([0, sampling_frequency / 2])

    fig.tight_layout()
    return fig

def show_components(S_: np.ndarray, freq_PSD: np.ndarray, PSD_components: np.ndarray, sampling_frequency: float, dimension_unit: str) -> Figure:
    """
    Displays the independent components obtained from ICA in a grid layout.
    Each component is shown in both time-domain and frequency-domain plots.

    Args:
        S_ (np.ndarray): The independent components (sources).
        freq_PSD (np.ndarray): The frequency bins for the power spectral density.
        PSD_components (np.ndarray): The power spectral density of the components.
        sampling_frequency (float): Sampling rate in Hz.
        dimension_unit (str): Unit of the signal amplitude (e.g., 'uV').

    Returns:
        Figure: A Matplotlib Figure object containing the plots of independent components.
    """
    n_components = S_.shape[0]
    fig, ax = plt.subplots(n_components, 2, figsize=(14, 3.5*n_components), dpi=150)

    # Generate precise axes
    t_axis = np.linspace(0, S_.shape[1] / sampling_frequency, S_.shape[1])

    for idx in range(n_components):
        # --- PLOT 1: TIME DOMAIN ---
        ax[idx, 0].plot(t_axis, S_[idx, :], linewidth=0.5)
        ax[idx, 0].set_title(f"Independent Component {idx+1} - Time Domain")
        ax[idx, 0].set_xlabel("Time (s)")
        ax[idx, 0].set_ylabel(dimension_unit)
        ax[idx, 0].set_xlim([0, S_.shape[1] / sampling_frequency])
        ax[idx, 0].grid(True, linestyle="--", alpha=0.6)

        # --- PLOT 2: FREQUENCY DOMAIN ---
        ax[idx, 1].semilogy(freq_PSD, PSD_components[idx, :], linewidth=0.5)
        ax[idx, 1].set_title(f"Independent Component {idx+1} - Frequency Domain - PSD")
        ax[idx, 1].set_xlabel("Frequency (Hz)")
        ax[idx, 1].set_ylabel("PSD")
        ax[idx, 1].set_xlim([0, min(60, sampling_frequency / 2)])  # Limit to 60 Hz or Nyquist frequency for EEG relevance
        ax[idx, 1].grid(True, linestyle="--", alpha=0.6)

    fig.tight_layout()
    return fig

def display_PSD(freq_PSD: np.ndarray, PSD_data: np.ndarray, channel_names: list) -> Figure:
    """
    Displays the Power Spectral Density (PSD) for all channels in a grid layout.

    Args:
        freq_PSD (np.ndarray): The frequency bins for the power spectral density.
        PSD_data (np.ndarray): The power spectral density of the channels.
        channel_names (list): List of channel names corresponding to the PSD data.

    Returns:
        Figure: A Matplotlib Figure object containing the PSD plots for all channels.
    """

    lobes = {"Frontal": [i for i, name in enumerate(channel_names) if name.upper().startswith(('F', 'AF', 'FP'))],
             "Central": [i for i, name in enumerate(channel_names) if name.upper().startswith('C')],
             "Temporal": [i for i, name in enumerate(channel_names) if name.upper().startswith('T')],
             "Parietal": [i for i, name in enumerate(channel_names) if name.upper().startswith('P')],
             "Occipital": [i for i, name in enumerate(channel_names) if name.upper().startswith(('O','I'))]
            }

    # Filter out empty lobes to avoid plotting blank graphs
    lobes = {k: v for k, v in lobes.items() if len(v) > 0}
    n_lobes = len(lobes)

    
    fig, ax = plt.subplots(n_lobes, 1, figsize=(14, 3.5*n_lobes), dpi=150, squeeze=False)

    for idx, (lobe_name, channels) in enumerate(lobes.items()):

        for ch in channels:
            ax[idx, 0].semilogy(freq_PSD, PSD_data[ch, :], linewidth=0.5, alpha=0.7)
            
        ax[idx, 0].set_title(f"Power Spectral Density - {lobe_name} Lobe")
        ax[idx, 0].set_xlabel("Frequency (Hz)")
        ax[idx, 0].set_ylabel("PSD")
        ax[idx, 0].set_xlim([0, 60.0])  # Limit to 60 Hz for EEG relevance
        ax[idx, 0].grid(True, linestyle="--", alpha=0.6)
        #ax[idx, 0].legend([channel_names[ch] for ch in channels], loc='upper right', fontsize='small')

    fig.tight_layout()
    return fig


def scalp_map(montage_dict: dict) -> Figure:
    """
    Draws a topographic map of EEG electrode positions based on the provided montage dictionary
    using Matplotlib for perfect static rendering and printing.
    """
    # Create the figure with a defined resolution
    fig, ax = plt.subplots(figsize=(6, 6), dpi=150)

    # 1. Draw the head outline (a perfect circle)
    head_circle = patches.Circle((0, 0), radius=1.0, edgecolor='black', facecolor='none', linewidth=2)
    ax.add_patch(head_circle)

    # 2. Draw the nose
    ax.plot([-0.1, 0, 0.1], [0.98, 1.15, 0.98], color='black', linewidth=2)

    # 3. Draw the ears using quadratic Bezier curves (Path)
    # Left ear
    verts_left = [(-0.98, 0.15), (-1.15, 0), (-0.98, -0.15)]
    codes = [Path.MOVETO, Path.CURVE3, Path.CURVE3]
    path_left = Path(verts_left, codes)
    ax.add_patch(patches.PathPatch(path_left, edgecolor='black', facecolor='none', linewidth=2))

    # Right ear
    verts_right = [(0.98, 0.15), (1.15, 0), (0.98, -0.15)]
    path_right = Path(verts_right, codes)
    ax.add_patch(patches.PathPatch(path_right, edgecolor='black', facecolor='none', linewidth=2))

    # 4. Extract electrode coordinates from the montage dictionary
    labels = list(montage_dict.keys())
    x_coords = [coords[0] for coords in montage_dict.values()]
    y_coords = [coords[1] for coords in montage_dict.values()]

    # Add electrodes as a scatter plot
    ax.scatter(x_coords, y_coords, s=60, color='blue', edgecolor='darkslategray', linewidth=1.5, zorder=3)

    # Add text labels above each electrode
    for label, x, y in zip(labels, x_coords, y_coords):
        ax.text(x, y + 0.05, label, fontsize=9, ha='center', va='bottom', zorder=4)

    # 5. Final axis settings
    ax.set_aspect('equal', adjustable='box') # Force 1:1 aspect ratio
    ax.axis('off') # Hide axes and grid

    # Generous limits to ensure the nose and outer labels are not clipped
    ax.set_xlim(-1.4, 1.4)
    ax.set_ylim(-1.4, 1.4)
    
    # Remove superfluous margins
    fig.tight_layout()

    return fig