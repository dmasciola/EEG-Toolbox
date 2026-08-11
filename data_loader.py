import pyedflib
import numpy as np


def load_edf_data(file_path):   

    print(f"\nLoading: {file_path}\n")

    f = pyedflib.EdfReader(file_path)

    n_channels = f.signals_in_file

    channel_names = f.getSignalLabels()

    sample_frequency = f.getSampleFrequency(0)

    sampling_time = f.getFileDuration()

    n_samples = int(f.getNSamples()[0])

    data_array = np.zeros((n_channels, n_samples))

    data_dimension = f.getPhysicalDimension(1)

    for i in range(n_channels):
        data_array[i, :] = f.readSignal(i)

    f._close()
    
    print("Data loaded!\n")

    return data_array, n_channels, channel_names, sample_frequency, sampling_time, data_dimension

