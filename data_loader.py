import pyedflib as edf
import numpy as np
from typing import Tuple, List

"""
This module provides functions to load, download and extract data from EEG files in EDF (European Data Format).
The module is currently designed to handle files with uniform sampling rates across all channels. 
It extracts the signal data, channel information, sampling frequency, 
and other relevant metadata for further processing and analysis.
"""

def load_edf_data(file_path: str, verbose: bool = False) -> Tuple[np.ndarray, int, List[str], float, int, str]:
    """
    Loads and extracts data from an EEG file in EDF (European Data Format).

    Args:
        file_path (str): The physical path (absolute or temporary) of the .edf file.
        verbose (bool, optional): If True, prints execution progress. Defaults to False.

    Returns:
        Tuple[np.ndarray, int, List[str], float, int, str]:
            - data_array: 2D array (N_channels x N_samples) containing the signals.
            - n_channels: Total number of recorded channels.
            - channel_names: List containing the labels of each channel.
            - sample_frequency: Sampling frequency of the signal in Hz.
            - sampling_time: Total duration of the recording in seconds.
            - data_dimension: Physical dimension/unit of the data (e.g., 'uV').

    Raises:
        OSError: If the file is not found or is unreadable.
        Exception: For internal pyedflib decoding errors.
    """
    
    # Helper function to handle logging without repeating "if verbose:"
    def log(message: str):
        if verbose:
            print(message)

    f = None
    try:
        log(f"Loading EDF file: {file_path}...")
        
        # Initialize the EDF reader
        f = edf.EdfReader(file_path)

        # Extract global metadata
        n_channels = f.signals_in_file
        channel_names = f.getSignalLabels()
        
        # Assume uniform sampling and dimensions by referencing the first channel (index 0)

        n_samples_array = f.getNSamples()

        if not np.all(n_samples_array == n_samples_array[0]):
            raise ValueError("The EDF file contains channels with heterogeneous sampling rates. The toolbox currently requires uniform sampling across all channels.")
        n_samples = int(n_samples_array[0])
        sample_frequency = f.getSampleFrequency(0)
        sampling_time = f.getFileDuration()

        data_dimension = f.getPhysicalDimension(0)

        log(f"Extracting {n_channels} channels...")
        
        # Pre-allocate the matrix to optimize memory usage
        data_array = np.zeros((n_channels, n_samples))

        # Populate the matrix channel by channel
        for i in range(n_channels):
            data_array[i, :] = f.readSignal(i)

        log("Data loaded successfully!\n")

        return data_array, n_channels, channel_names, sample_frequency, sampling_time, data_dimension

    finally:
        # The finally block ensures the file is safely closed and cleared from RAM
        if f is not None:
            f.close()


def export_to_EDF(file_path: str, data: np.ndarray, channel_names: list, sampling_frequency: float, dimension_unit: str = 'uV') -> None:
    """
    Exports the processed EEG data matrix back to a standard European Data Format (.edf) file.

    Args:
        file_path (str): The destination file path.
        data (np.ndarray): The processed signal data matrix.
        channel_names (list): List of channel names.
        sampling_frequency (float): Sampling rate in Hz.
        dimension_unit (str): Unit of the signal amplitude (e.g., 'uV').
    """

    # Create the signal headers dynamically
    signal_headers = edf.highlevel.make_signal_headers(
        channel_names, 
        dimension_unit, 
        sampling_frequency,
        physical_min = np.min(data),
        physical_max = np.max(data)
    )
    
    # Write the data array to the .edf file
    edf.highlevel.write_edf(file_path, data, signal_headers)