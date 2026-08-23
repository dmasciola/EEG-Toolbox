import numpy as np
from scipy import signal
from typing import Tuple
import sklearn as sk
import streamlit as st

"""
This module provides a suite of signal processing functions for EEG data analysis,
including FIR filter design, 
filtering, 
downsampling, 
ICA, 
and PSD computation.

@st.cache_data is used to cache the results of functions that are computationally 
expensive and have deterministic outputs, improving performance in interactive applications.
"""


def estimate_kaiser_beta(order: int, transition_width: float, frequency: float) -> float:
    """
    Estimates the beta parameter for a Kaiser window based on desired attenuation.

    Args:
        order (int): The baseline order of the filter.
        transition_width (float): The width of the transition band in Hz.
        frequency (float): The sampling frequency in Hz.

    Returns:
        beta (float): The calculated beta parameter.
    """
    if order % 2 == 1: 
        order += 1
        
    attenuation = signal.kaiser_atten(order + 1, 2 * transition_width / frequency * np.pi)
    beta = float(signal.kaiser_beta(attenuation))
    
    return beta

@st.cache_data
def Fir_designer(frequency: float, order: int, filter_selected: str, method: str,
                 f_cut_low: float, f_cut_high: float, trans_width: float,
                 window_selected: str, beta: float) -> np.ndarray:
    """
    Synthesizes a digital FIR filter using Windowed, Equiripple (Parks-McClellan), or Least Squares methods.

    Args:
        frequency (float): Sampling frequency in Hz.
        order (int): Desired filter order (will be dynamically adjusted to ensure Type-I linear phase).
        filter_selected (str): Filter topology ('Highpass Filter', 'Lowpass Filter', etc.).
        method (str): Synthesis method ('Window Method', 'Equiripple', 'Least Squares').
        f_cut_low (float): Lower cutoff frequency in Hz.
        f_cut_high (float): Upper cutoff frequency in Hz.
        trans_width (float): Transition band width in Hz (used for Equiripple and Least Squares).
        window_selected (str): Window type if using Window Method (e.g., 'Kaiser', 'Hanning').
        beta (float): Kaiser window beta parameter (ignored for other windows).

    Returns:
        Fir_filter (np.ndarray): A 1D array of the generated FIR filter coefficients (taps).
    """
    # Ensure an odd number of taps (even order) to force a Type-I linear-phase FIR filter
    n_taps = order + 1
    n_taps += (n_taps + 1) % 2
    
    nyquist = 0.5 * frequency

    match method:
        case "Window Method":
            # Dynamically map the UI window string to the SciPy window parameter (DRY principle)
            if window_selected == "Kaiser":
                win = ('kaiser', beta)
            elif window_selected == "Hanning":
                win = 'hann'
            else:
                win = window_selected.lower() # 'hamming', 'blackman'
                
            match filter_selected:
                case "Highpass Filter":
                    return signal.firwin(n_taps, f_cut_high, fs=frequency, window=win, pass_zero=False)
                case "Lowpass Filter":
                    return signal.firwin(n_taps, f_cut_low, fs=frequency, window=win, pass_zero=True)
                case "Bandpass Filter":
                    return signal.firwin(n_taps, [f_cut_low, f_cut_high], fs=frequency, window=win, pass_zero=False)
                case "Notch Filter":
                    return signal.firwin(n_taps, [f_cut_low, f_cut_high], fs=frequency, window=win, pass_zero=True)

        case "Equiripple":
            match filter_selected:
                case "Highpass Filter":
                    return signal.remez(n_taps, [0, f_cut_high - trans_width, f_cut_high, nyquist], [0, 1], fs=frequency)
                case "Lowpass Filter":
                    return signal.remez(n_taps, [0, f_cut_low, f_cut_low + trans_width, nyquist], [1, 0], fs=frequency)
                case "Bandpass Filter":
                    return signal.remez(n_taps, [0, f_cut_low - trans_width, f_cut_low, f_cut_high, f_cut_high + trans_width, nyquist], [0, 1, 0], fs=frequency)
                case "Notch Filter":
                    return signal.remez(n_taps, [0, f_cut_low - trans_width, f_cut_low, f_cut_high, f_cut_high + trans_width, nyquist], [1, 0, 1], fs=frequency)

        case "Least Squares":
            match filter_selected:
                case "Highpass Filter":
                    return signal.firls(n_taps, [0, f_cut_high - trans_width, f_cut_high, nyquist], [0, 0, 1, 1], fs=frequency)
                case "Lowpass Filter":
                    return signal.firls(n_taps, [0, f_cut_low, f_cut_low + trans_width, nyquist], [1, 1, 0, 0], fs=frequency)
                case "Bandpass Filter":
                    return signal.firls(n_taps, [0, f_cut_low - trans_width, f_cut_low, f_cut_high, f_cut_high + trans_width, nyquist], [0, 0, 1, 1, 0, 0], fs=frequency)
                case "Notch Filter":
                    return signal.firls(n_taps, [0, f_cut_low - trans_width, f_cut_low, f_cut_high, f_cut_high + trans_width, nyquist], [1, 1, 0, 0, 1, 1], fs=frequency)
    
    raise ValueError("Invalid filter configuration provided.")

@st.cache_data
def Filter_data(data: np.ndarray, Fir_filter: np.ndarray) -> np.ndarray:
    """
    Applies a zero-phase digital filter to the signal data using forward-backward filtering.

    Args:
        data (np.ndarray): the signal matrix.
        Fir_filter (np.ndarray): Designed Fir Filter components.

    Returns
        filtered_data (ndp.ndarray): filtered data with zero-phase
    """
    return signal.filtfilt(Fir_filter, 1.0, data)


def Current_Remover(data: np.ndarray, frequency: float, f_remove: float, Q: float) -> np.ndarray:
    """
    Generates and applies an Infinite Impulse Response (IIR) notch filter to remove powerline artifacts.

    Args:
        data (nd.array): the signal matrix.
        frequency (float): sampling frequency.
        f_remove (float): current artifact frequency.
        Q (float): quality factor fo IIR Notch filter.

    Returns:
        filtered_data (np.ndarray): filtered signal with iirnotch filter.
    """
    b, a = signal.iirnotch(f_remove, Q, fs=frequency)
    return signal.filtfilt(b, a, data)


def Frequency_response(Fir_filter: np.ndarray, frequency: float) -> Tuple[np.ndarray, np.ndarray]:
    """
    Computes the frequency response of the digital filter for Bode plotting.

    Args:
        Fir_filter (np.ndarray): Designed Fir Filter components.
        frequency (float): sampling frequency

    Returns:
        frequency_response (np.ndarray): complex matrix with frequency response of the filter.
    """
    return signal.freqz(Fir_filter, 1, fs=frequency)

@st.cache_data
def Downsample(data: np.ndarray, downsample_factor: int) -> np.ndarray:
    """
    Downsamples the input data by the specified factor.

    Args:
        data (np.ndarray): The input signal data to be downsampled.
        downsample_factor (int): The factor by which to downsample the data.

    Returns:
        data_downsampled (np.ndarray): The downsampled signal data.
    """
    return signal.decimate(data, downsample_factor, ftype='iir', zero_phase=True)


def Remove_bad_channels(data: np.ndarray, bad_channels: list) -> np.ndarray:
    """
    Removes selected bad channels from the input signal data.

    Args:
        data (np.ndarray): The input signal data with multiple channels.
        bad_channels (list): A list of indices for the channels to be removed.

    Returns:
        data_clean (np.ndarray): The signal data with bad channels set to zero. (to later interpolate)
    """

    data_clean = data.copy()

    for channel in bad_channels:
        data_clean[channel, :] = 0  # Set bad channels to zero
    
    # Return lean data sets
    return data_clean


def Interpolate_bad_channels(data: np.ndarray, channel_names: list, bad_channels: list, electrode_layout: dict) -> np.ndarray:
    """
    Interpolates the signal data for the specified bad channels using Inverse Distance Weighting Interpolation.

    Args:
        data (np.ndarray): The input signal data with multiple channels.
        channel_names (list): A list of channel names.
        bad_channels (list): A list of indices for the channels to be interpolated.
        electrode_layout (dict): A dictionary mapping channel names to their (x, y) coordinates.    

    Returns:
        data_interpolated (np.ndarray): The signal data with bad channels interpolated.
    """
    data_interpolated = data.copy()
    good_channels = [i for i in range(data.shape[0]) if i not in bad_channels]

    for channel in bad_channels:
        weights = np.zeros(data.shape[0])
        bad_coord = np.array(electrode_layout.get(channel_names[channel], (0, 0)))
        for ch in good_channels:
            good_coord = np.array(electrode_layout.get(channel_names[ch], (0, 0)))
            weights[ch] = 1/(np.linalg.norm(bad_coord - good_coord) + 1e-10)**2

        data_interpolated[channel, :] = np.sum(data[good_channels, :] * weights[good_channels, np.newaxis], axis=0) / np.sum(weights[good_channels])
    return data_interpolated


def Common_average_reference(data: np.ndarray) -> np.ndarray:
    """
    Applies Common Average Referencing (CAR) to the input signal data.

    Args:
        data (np.ndarray): The input signal data with multiple channels.

    Returns:
        data - mean_signal (np.ndarray): The signal data after applying CAR.
    """
    mean_signal = np.mean(data, axis=0)
    return data - mean_signal

@st.cache_data
def Compute_ICA(data: np.ndarray, n_components: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Performs Independent Component Analysis (ICA) on the input signal data.

    Args:
        data (np.ndarray): The input signal data with multiple channels.
        n_components (int): The number of independent components to extract.

    Returns:
        S_T (np.ndarray): The independent components.
        A_ (np.ndarray): The mixing matrix.
        data_mean (np.ndarray): mean of every channel.
    """
    ica = sk.decomposition.FastICA(n_components=n_components, random_state=0)
    data_mean = np.mean(data, axis=1)  # Get the mean of the data
    S_ = ica.fit_transform(data.T)  # Reconstruct signals
    A_ = ica.mixing_  # Get estimated mixing matrix
    return S_.T, A_, data_mean


def Reconstruct_from_ICA(S_: np.ndarray, A_: np.ndarray, data_mean: np.ndarray, bad_components: list) -> np.ndarray:
    """
    Reconstructs the signal after removing specified independent components.

    Args:
        S_ (np.ndarray): The independent components.
        A_ (np.ndarray): The mixing matrix.
        data_mean (np.ndarray): The mean of the original data.
        bad_components (list): A list of indices for the components to be removed.

    Returns:
        reconstructed_signal (np.ndarray): The reconstructed signal after removing bad components.
    """
    S_clean = S_.copy()

    for bad_idx in bad_components:
        S_clean[bad_idx-1, :] = 0  # Zero out bad components

    reconstructed_signal = np.dot(A_, S_clean) + data_mean[:, np.newaxis]
    return reconstructed_signal


def Compute_PSD(data: np.ndarray, sampling_frequency: float) -> Tuple[np.ndarray, np.ndarray]:
    """
    Computes the Power Spectral Density (PSD) of the input signal data using Welch's method.

    Args:
        data (np.ndarray): The input signal data with multiple channels.
        sampling_frequency (float): The sampling frequency of the signal in Hz.

    Returns:
        freqs (np.ndarray): frequency bins.
        psd (np.ndarray): Power Spectral Density values corresponding to the bins.
    """
    freqs, psd = signal.welch(data, fs=sampling_frequency, nperseg=1024)
    return freqs, psd