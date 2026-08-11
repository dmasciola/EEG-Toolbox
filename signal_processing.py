from scipy import fft, signal
import numpy as np

def estimate_kaiser_beta(order, transition_width,frequency):
    if order%2 == 1: order +=1
    attenuation = signal.kaiser_atten(order+1, 2*transition_width/frequency*np.pi)
    beta = signal.kaiser_beta(attenuation)

    return beta


def Fir_designer(frequency,order,filter_selected,method,f_cut_low,f_cut_high,trans_width,window_selected,beta):

    # Use an odd number of taps (Type-I linear-phase FIR)
    n_taps = order + 1
    n_taps += (n_taps+1)%2

    match method:
        case "Window Method":

            match window_selected:
                case "Kaiser": 

                    match filter_selected:
                        case "Highpass Filter":
                            Fir_filter = signal.firwin(n_taps,f_cut_high,fs = frequency, window = ('kaiser', beta), pass_zero=False)
                        case "Lowpass Filter":
                            Fir_filter = signal.firwin(n_taps,f_cut_low,fs = frequency, window = ('kaiser', beta), pass_zero=True)
                        case "Bandpass Filter":
                            f_band = [f_cut_low,f_cut_high]
                            Fir_filter = signal.firwin(n_taps,f_band,fs = frequency, window = ('kaiser', beta), pass_zero=False)
                        case "Notch Filter":
                            f_remove = [f_cut_low,f_cut_high]
                            Fir_filter = signal.firwin(n_taps,f_remove,fs = frequency, window = ('kaiser', beta), pass_zero=True)

                case "Hanning":

                    win = 'hann'
                    match filter_selected:
                        case "Highpass Filter":
                            Fir_filter = signal.firwin(n_taps,f_cut_high,fs = frequency, window = win, pass_zero=False)
                        case "Lowpass Filter":
                            Fir_filter = signal.firwin(n_taps,f_cut_low,fs = frequency, window = win, pass_zero=True)
                        case "Bandpass Filter":
                            f_band = [f_cut_low,f_cut_high]
                            Fir_filter = signal.firwin(n_taps,f_band,fs = frequency, window = win, pass_zero=False)
                        case "Notch Filter":
                            f_remove = [f_cut_low,f_cut_high]
                            Fir_filter = signal.firwin(n_taps,f_remove,fs = frequency, window = win, pass_zero=True)       

                case "Hamming":

                    win = 'hamming'
                    match filter_selected:
                        case "Highpass Filter":
                            Fir_filter = signal.firwin(n_taps,f_cut_high,fs = frequency, window = win, pass_zero=False)
                        case "Lowpass Filter":
                            Fir_filter = signal.firwin(n_taps,f_cut_low,fs = frequency, window = win, pass_zero=True)
                        case "Bandpass Filter":
                            f_band = [f_cut_low,f_cut_high]
                            Fir_filter = signal.firwin(n_taps,f_band,fs = frequency, window = win, pass_zero=False)
                        case "Notch Filter":
                            f_remove = [f_cut_low,f_cut_high]
                            Fir_filter = signal.firwin(n_taps,f_remove,fs = frequency, window = win, pass_zero=True)       

                case "Blackman":

                    win = 'blackman'
                    match filter_selected:
                        case "Highpass Filter":
                            Fir_filter = signal.firwin(n_taps,f_cut_high,fs = frequency, window = win, pass_zero=False)
                        case "Lowpass Filter":
                            Fir_filter = signal.firwin(n_taps,f_cut_low,fs = frequency, window = win, pass_zero=True)
                        case "Bandpass Filter":
                            f_band = [f_cut_low,f_cut_high]
                            Fir_filter = signal.firwin(n_taps,f_band,fs = frequency, window = win, pass_zero=False)
                        case "Notch Filter":
                            f_remove = [f_cut_low,f_cut_high]
                            Fir_filter = signal.firwin(n_taps,f_remove,fs = frequency, window = win, pass_zero=True)     

        case "Equiripple":

            match filter_selected:
                case "Highpass Filter":
                    Fir_filter = signal.remez(n_taps,
                                              [0, f_cut_high - trans_width, f_cut_high, 0.5*frequency],
                                              [0,1],
                                              fs=frequency
                                              )
                case "Lowpass Filter":
                    Fir_filter = signal.remez(n_taps,
                                              [0, f_cut_low, f_cut_low + trans_width, 0.5*frequency],
                                              [1,0],
                                              fs=frequency
                                              )
                case "Bandpass Filter":
                    Fir_filter = signal.remez(n_taps,
                                              [0, f_cut_low - trans_width, f_cut_low, f_cut_high, f_cut_high + trans_width, 0.5*frequency],
                                              [0,1,0],
                                              fs=frequency
                                              )
                case "Notch Filter":
                    Fir_filter = signal.remez(n_taps,
                                              [0, f_cut_low - trans_width, f_cut_low, f_cut_high, f_cut_high + trans_width, 0.5*frequency],
                                              [1,0,1],
                                              fs=frequency
                                              )     

        case "Least Squares":

            match filter_selected:
                case "Highpass Filter":
                    Fir_filter = signal.firls(n_taps,
                                              [0, f_cut_high - trans_width, f_cut_high, 0.5*frequency],
                                              [0,0,1,1],
                                              fs=frequency
                                              )
                case "Lowpass Filter":
                    Fir_filter = signal.firls(n_taps,
                                              [0, f_cut_low, f_cut_low + trans_width, 0.5*frequency],
                                              [1,1,0,0],
                                              fs=frequency
                                              )     
                case "Bandpass Filter":
                    Fir_filter = signal.firls(n_taps,
                                              [0, f_cut_low - trans_width, f_cut_low, f_cut_high, f_cut_high + trans_width, 0.5*frequency],
                                              [0,0,1,1,0,0],
                                              fs=frequency
                                              )
                case "Notch Filter":
                    Fir_filter = signal.firls(n_taps,
                                              [0, f_cut_low - trans_width, f_cut_low, f_cut_high, f_cut_high + trans_width, 0.5*frequency],
                                              [1,1,0,0,1,1],
                                              fs=frequency
                                              )    

    return Fir_filter                         

def Filter_data(data, Fir_filter):

    return signal.filtfilt(Fir_filter, 1.0, data)
                             
                        
"""

def Fir_win_lowpass(data,frequency,order,f_cut_low,window_selected,beta):

    if order%2 == 1: order += 1    # Ensure an even filter order so that the number of taps is odd.
                                   # This is required for the chosen linear-phase FIR configuration.

    match window_selected:

        case "Kaiser":
                
            Fir_filter = signal.firwin(order+1,f_cut_low,fs = frequency, window = ('kaiser', beta), pass_zero=True)

        case "Hanning":

            Fir_filter = signal.firwin(order+1,f_cut_low,fs = frequency, window = 'hann', pass_zero=True)

        case "Hamming":

            Fir_filter = signal.firwin(order+1,f_cut_low,fs = frequency, window = 'hamming', pass_zero=True)

        case "Blackman":

            Fir_filter = signal.firwin(order+1,f_cut_low,fs = frequency, window = 'blackman', pass_zero=True)

    filtered_data = signal.filtfilt(Fir_filter, 1.0, data)

    return filtered_data, Fir_filter

def Fir_win_highpass(data,frequency,order,f_cut_high,window_selected,beta):

    if order%2 == 1: order += 1   

    match window_selected:

        case "Kaiser":
                
            Fir_filter = signal.firwin(order+1,f_cut_high,fs = frequency, window = ('kaiser', beta), pass_zero=False)

        case "Hanning":

            Fir_filter = signal.firwin(order+1,f_cut_high,fs = frequency, window = 'hann', pass_zero=False)

        case "Hamming":

            Fir_filter = signal.firwin(order+1,f_cut_high,fs = frequency, window = 'hamming', pass_zero=False)

        case "Blackman":

            Fir_filter = signal.firwin(order+1,f_cut_high,fs = frequency, window = 'blackman', pass_zero=False)

    filtered_data = signal.filtfilt(Fir_filter, 1.0, data)

    return filtered_data, Fir_filter

def Fir_win_bandpass(data,frequency,order,f_pass,bandwidth,window_selected,beta):

    if order%2 == 1: order += 1 

    f_band = [f_pass - bandwidth/2, f_pass + bandwidth/2]

    match window_selected:

        case "Kaiser":
                
            Fir_filter = signal.firwin(order+1,f_band,fs = frequency, window = ('kaiser', beta), pass_zero=False)

        case "Hanning":

            Fir_filter = signal.firwin(order+1,f_band,fs = frequency, window = 'hann', pass_zero=False)

        case "Hamming":

            Fir_filter = signal.firwin(order+1,f_band,fs = frequency, window = 'hamming', pass_zero=False)

        case "Blackman":

            Fir_filter = signal.firwin(order+1,f_band,fs = frequency, window = 'blackman', pass_zero=False)

    filtered_data = signal.filtfilt(Fir_filter, 1.0, data)

    return filtered_data, Fir_filter

def Fir_win_notch(data,frequency,order,f_remove,bandwidth,window_selected,beta):

    if order%2 == 1: order += 1  

    f_notch = [f_remove - bandwidth/2, f_remove + bandwidth/2]

    match window_selected:

        case "Kaiser":
                
            Fir_filter = signal.firwin(order+1,f_notch,fs = frequency, window = ('kaiser', beta), pass_zero=True)

        case "Hanning":

            Fir_filter = signal.firwin(order+1,f_notch,fs = frequency, window = 'hann', pass_zero=True)

        case "Hamming":

            Fir_filter = signal.firwin(order+1,f_notch,fs = frequency, window = 'hamming', pass_zero=True)

        case "Blackman":

            Fir_filter = signal.firwin(order+1,f_notch,fs = frequency, window = 'blackman', pass_zero=True)
    
    filtered_data = signal.filtfilt(Fir_filter, 1.0, data)

    return filtered_data, Fir_filter


    

def Fir_eqripp_highpass(data,frequency,order,f_cut_high,trans_width):

    if order%2 == 1: order +=1

    Fir_filter = signal.remez(order +1,
                              [0, f_cut_high - trans_width, f_cut_high, 0.5*frequency],
                              [0,1],
                              fs=frequency
                              )
    filtered_data = signal.filtfilt(Fir_filter, 1.0, data)

    return filtered_data, Fir_filter

def Fir_eqripp_lowpass(data,frequency,order,f_cut_low,trans_width):

    if order%2 == 1: order +=1

    Fir_filter = signal.remez(order +1,
                              [0, f_cut_low, f_cut_low + trans_width, 0.5*frequency],
                              [1,0],
                              fs=frequency
                              )
    filtered_data = signal.filtfilt(Fir_filter, 1.0, data)

    return filtered_data, Fir_filter

def Fir_eqripp_bandpass(data,frequency,order,f_pass,bandwidth,trans_width):

    if order%2 == 1: order +=1

    f_band = [f_pass - bandwidth/2, f_pass + bandwidth/2]

    Fir_filter = signal.remez(order +1,
                              [0, f_band[0] - trans_width, f_band[0], f_band[1], f_band[1] + trans_width, 0.5*frequency],
                              [0,1,0],
                              fs=frequency
                              )
    filtered_data = signal.filtfilt(Fir_filter, 1.0, data)

    return filtered_data, Fir_filter

def Fir_eqripp_notch(data,frequency,order,f_remove,bandwidth,trans_width):

    if order%2 == 1: order +=1

    f_band = [f_remove - bandwidth/2, f_remove + bandwidth/2]

    Fir_filter = signal.remez(order +1,
                              [0, f_band[0] - trans_width, f_band[0], f_band[1], f_band[1] + trans_width, 0.5*frequency],
                              [1,0,1],
                              fs=frequency
                              )
    filtered_data = signal.filtfilt(Fir_filter, 1.0, data)

    return filtered_data, Fir_filter



def Fir_lsquares_highpass(data,frequency,order,f_cut_high,trans_width):

    if order%2 == 1: order +=1

    Fir_filter = signal.firls(order +1,
                              [0, f_cut_high-trans_width, f_cut_high, 0.5*frequency],
                              [0,0,1,1],
                              fs=frequency
                              )
    
    filtered_data = signal.filtfilt(Fir_filter, 1.0, data)

    return filtered_data, Fir_filter

def Fir_lsquares_lowpass(data,frequency,order,f_cut_low,trans_width):

    if order%2 == 1: order +=1

    Fir_filter = signal.firls(order +1,
                              [0, f_cut_low, f_cut_low + trans_width, 0.5*frequency],
                              [1,1,0,0],
                              fs=frequency
                              )
    filtered_data = signal.filtfilt(Fir_filter, 1.0, data)

    return filtered_data, Fir_filter

def Fir_lsquares_bandpass(data,frequency,order,f_pass,bandwidth,trans_width):

    if order%2 == 1: order +=1

    f_band = [f_pass - bandwidth/2, f_pass + bandwidth/2]

    Fir_filter = signal.firls(order +1,
                              [0, f_band[0] - trans_width, f_band[0], f_band[1], f_band[1] + trans_width, 0.5*frequency],
                              [0,0,1,1,0,0],
                              fs=frequency
                              )
    filtered_data = signal.filtfilt(Fir_filter, 1.0, data)

    return filtered_data, Fir_filter

def Fir_lsquares_notch(data,frequency,order,f_remove,bandwidth,trans_width):
    
    if order%2 == 1: order +=1

    f_band = [f_remove - bandwidth/2, f_remove + bandwidth/2]

    Fir_filter = signal.firls(order +1,
                              [0, f_band[0] - trans_width, f_band[0], f_band[1], f_band[1] + trans_width, 0.5*frequency],
                              [1,1,0,0,1,1],
                              fs=frequency
                              )
    filtered_data = signal.filtfilt(Fir_filter, 1.0, data)

    return filtered_data, Fir_filter

"""
    
def Current_Remover(data,frequency,f_remove,Q):

    b, a = signal.iirnotch(f_remove, Q, fs=frequency)
    current_filtered_data = signal.filtfilt(b, a, data)

    return current_filtered_data

def Frequency_response(Fir_filter,frequency):

    return signal.freqz(Fir_filter, 1, fs=frequency)
