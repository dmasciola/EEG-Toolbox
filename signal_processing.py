import numpy as np
from scipy import signal
from typing import Tuple

def estimate_kaiser_beta(order: int, transition_width: float, frequency: float) -> float:
    """
    Estimates the beta parameter for a Kaiser window based on desired attenuation.

    Args:
        order (int): The baseline order of the filter.
        transition_width (float): The width of the transition band in Hz.
        frequency (float): The sampling frequency in Hz.

    Returns:
        float: The calculated beta parameter.
    """
    if order % 2 == 1: 
        order += 1
        
    attenuation = signal.kaiser_atten(order + 1, 2 * transition_width / frequency * np.pi)
    beta = float(signal.kaiser_beta(attenuation))
    
    return beta


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
        np.ndarray: A 1D array of the generated FIR filter coefficients (taps).
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


def Filter_data(data: np.ndarray, Fir_filter: np.ndarray) -> np.ndarray:
    """
    Applies a zero-phase digital filter to the signal data using forward-backward filtering.
    """
    return signal.filtfilt(Fir_filter, 1.0, data)


def Current_Remover(data: np.ndarray, frequency: float, f_remove: float, Q: float) -> np.ndarray:
    """
    Generates and applies an Infinite Impulse Response (IIR) notch filter to remove powerline artifacts.
    """
    b, a = signal.iirnotch(f_remove, Q, fs=frequency)
    return signal.filtfilt(b, a, data)


def Frequency_response(Fir_filter: np.ndarray, frequency: float) -> Tuple[np.ndarray, np.ndarray]:
    """
    Computes the frequency response of the digital filter for Bode plotting.
    """
    return signal.freqz(Fir_filter, 1, fs=frequency)