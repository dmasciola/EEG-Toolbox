import matplotlib.pyplot as plt
import numpy as np
import signal_processing


def display_data(data,channel_name,sampling_time,sampling_frequency,dimension_unit,state):

    t_axis = np.linspace(0, sampling_time, len(data))

    f_axis = np.linspace(-sampling_frequency/2,(sampling_frequency-1)/2, len(data))

    
    fig, ax = plt.subplots(2, 1, figsize=(16,8), dpi=400)
   

    ax[0].plot(t_axis, data, color='b', linewidth=0.6)

    fourier_data = np.fft.fft(data)/len(data)                     #compute fast fourier transform
    fourier_data_shifted = np.fft.fftshift(fourier_data)    #shifts for plotting  
    ax[1].plot(f_axis, np.abs(fourier_data_shifted), color='b', linewidth=0.6)

    match state:

        case "filtered":
            ax[0].set_title(f"EEG - Channel {channel_name} - Post Processing - Time Domain")
            ax[1].set_title(f"EEG - Channel {channel_name} - Post Processing - Frequency Domain")

        case "default":
            ax[0].set_title(f"EEG - Channel {channel_name} - Time Domain")
            ax[1].set_title(f"EEG - Channel {channel_name} - Frequency Domain")

#--------TIME GRAPH SETTINGS--------
    ax[0].set_xlabel("Time (s)")
    ax[0].set_ylabel(dimension_unit)
    ax[0].grid(True, linestyle="--", alpha=0.6)
    ax[0].set_xlim([0,sampling_time])

#------FREQUENCY GRAPH SETTINGS-----
    ax[1].set_xlabel("Frequency (Hz)")
    ax[1].grid(True, linestyle="--", alpha=0.6)
    ax[1].set_xlim([-sampling_frequency/2,sampling_frequency/2])


    fig.tight_layout()

    return fig

def display_filter(filter,filter_selected,sampling_frequency,n):

    f_axis, h = signal_processing.Frequency_response(filter, sampling_frequency)


    fig, ax = plt.subplots(2, 1, figsize=(16,8), dpi=400)

    ax[0].set_title(f"Frequency Response of {filter_selected} FIR Filter (Magnitude)")
    ax[0].plot(f_axis, 20 * np.log10(abs(h)), 'C0')
    ax[0].set_ylabel("Amplitude in dB", color='C0')
    ax[0].grid(True)
    ax[0].axis('tight')
    ax[0].set(xlabel="Frequency in Hz")

    phase = np.unwrap(np.angle(h))
    ax[1].set_title(f"Frequency Response of {filter_selected} FIR Filter (Phase)")
    ax[1].plot(f_axis, phase, 'C1')
    ax[1].set_ylabel('Phase [rad]', color='C1')
    ax[1].grid(True)
    ax[1].axis('tight')

    fig.tight_layout()

    return fig



