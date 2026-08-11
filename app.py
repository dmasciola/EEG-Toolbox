import streamlit as st
from data_loader import load_edf_data
from data_displayer import display_data, display_filter
import signal_processing
import tempfile
from scipy import signal
import os


with st.sidebar:
    if st.button("Reset Toolbox", type="primary"):
        st.session_state.clear() # Clears session state memory
        st.rerun()

# Title of the app
st.title("EEG Toolbox")
st.caption("Developed by Davide Masciola | v1.0-beta")

if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False


uploaded_file = st.file_uploader("Upload EEG file", type=['edf'])

if uploaded_file is not None:

    with tempfile.NamedTemporaryFile(delete=False, suffix='.edf') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        temp_path = tmp_file.name #file physical path

    try:
        with st.spinner("Loading File..."):
            try:
                data_matrix, n_channels, channel_names, freq, time, dimension_unit = load_edf_data(temp_path)
        
                st.session_state.data_matrix = data_matrix
                st.session_state.n_channels = n_channels
                st.session_state.channel_names = channel_names
                st.session_state.freq = freq
                st.session_state.time = time
                st.session_state.dimension_unit = dimension_unit
        
                st.session_state.data_loaded = True    

            except Exception as e:
                st.error(f"An error occurred during loading: {e}")

            if st.session_state.data_loaded:

                st.success("Data extracted successfully!")

                st.text(f"\n--- DATA EXTRACTER ---")
                st.text(f"Sampling frequency: {st.session_state.freq} Hz")
                st.text(f"Sampling time: {st.session_state.time} s")
                st.text(f"Channels: {st.session_state.n_channels}")
                st.text(f"Channel names: {st.session_state.channel_names[:]}")
                #st.text(f"Data matrix dimensions: {st.session_state.data_matrix.shape} (Channels x Samples)")


                temp_channel = st.number_input(f"\nPlease select one channel to display (1 to {st.session_state.n_channels}): ",
                                                min_value = 1, 
                                                max_value = st.session_state.n_channels, 
                                                value=1
                                                )

                if st.button("Load Channel"):
                
                    st.session_state.channel_selected = temp_channel
                    st.session_state.data_selected = st.session_state.data_matrix[st.session_state.channel_selected - 1, :]
                    st.session_state.channel_selected_name = st.session_state.channel_names[st.session_state.channel_selected - 1]
                    st.success(f"Channel {st.session_state.channel_selected} loaded succesfully")

                if 'channel_selected' in st.session_state:
                
                    st.write("Orignial Signal")
                    st.pyplot(
                        display_data(st.session_state.data_selected,
                                st.session_state.channel_selected_name,
                                st.session_state.time,
                                st.session_state.freq,
                                st.session_state.dimension_unit,
                                state = "default"
                                ),
                                use_container_width=True
                             )

                    st.divider()
                    
                    st.write("Signal Processing")
                    st.write("Please select an option")
            
                    st.session_state.data_processing = st.session_state.data_selected.copy()
                    st.session_state.Fir_filter = None
                    
                    
                    if st.checkbox("1. Current Artifact Remover"):
                    
                        current_state = st.radio("Select Continent:", ['America (60 Hz)', 'Europe (50 Hz)'], index=None)    
                        f_current = None
                    
                        if current_state == 'America (60 Hz)':
                            f_current = 60   
                            Q = st.slider("Q:", min_value = f_current, max_value = f_current*100, value = f_current*10)                             
                            st.session_state.data_processing = signal_processing.Current_Remover(st.session_state.data_processing,
                                                                                                st.session_state.freq,
                                                                                                f_current,
                                                                                                Q
                                                                                                )
                                
                        elif current_state == 'Europe (50 Hz)':
                            f_current = 50
                            Q = st.slider("Q:", min_value = f_current, max_value = f_current*100, value = f_current*10)
                            st.session_state.data_processing = signal_processing.Current_Remover(st.session_state.data_processing,
                                                                                                st.session_state.freq,
                                                                                                f_current
                                                                                                )

                    if st.checkbox("2. Filter"):


                        filter_selected = st.radio("Select Filter:", ["Highpass Filter", "Lowpass Filter", "Bandpass Filter", "Notch Filter"])
                        method = st.radio("Filtering method:", ["Window Method", "Equiripple", "Least Squares"])
                        
                        if method == "Window Method":
                            
                            window_selected = st.radio("Window:",["Hanning", "Hamming", "Blackman", "Kaiser"])

                            if window_selected == "Kaiser":

                                order = st.number_input("Select Order:", min_value=2, max_value=int(1e4), value=201, step=2)

                            else:

                                order_method = st.radio("Filter Order:", ["Manual", "Auto"])

                                match order_method:

                                    case "Manual":

                                        order = st.number_input("Select Order:", min_value=2, max_value=int(1e4), value=201, step=2)
                                        
                                    case "Auto":

                                        factors = {"Hanning": 3.1, "Hamming": 3.3, "Blackman": 5.5}
                                        factor = factors.get(window_selected, 3.3)
    
                                        order = int(2* factor * st.session_state.freq)         #transition width is estimated to be 0.5 Hz
                            
                        try:
                            match filter_selected:

                                case "Highpass Filter":

                                    f_cut_h = st.slider("Cutoff frequency:", min_value = 0.5, max_value = 0.45*st.session_state.freq, value = 0.5)
                                    f_cut_l = None 

                                    match method:

                                        case "Window Method":

                                            if window_selected == "Kaiser":

                                                trans_width = st.slider("Transition Width:", min_value = 0.05, max_value = f_cut_h - 0.025, value = 0.05)

                                                beta = signal_processing.estimate_kaiser_beta(order, trans_width, st.session_state.freq)

                                                st.session_state.Fir_filter = signal_processing.Fir_designer(st.session_state.freq,
                                                                                                             order,
                                                                                                             filter_selected,
                                                                                                             method,
                                                                                                             f_cut_l,
                                                                                                             f_cut_h,
                                                                                                             trans_width,
                                                                                                             window_selected,
                                                                                                             beta
                                                                                                             )
                                                
                                            else:         

                                                trans_width = None
                                                st.session_state.Fir_filter = signal_processing.Fir_designer(st.session_state.freq,
                                                                                                             order,
                                                                                                             filter_selected,
                                                                                                             method,
                                                                                                             f_cut_l,
                                                                                                             f_cut_h,
                                                                                                             trans_width,
                                                                                                             window_selected,
                                                                                                             beta = None,
                                                                                                             )

                                        case "Equiripple":

                                            #atten_cut = st.number_input("Attenuation in Cutoff Region:", min_value=0, max_value=1, value=0)
                                            #gain_pass = st.number_input("Gain in Pass Region:", min_value=1)
                                            trans_width = st.slider("Transition Width:", min_value = 0.2, max_value = f_cut_h - 0.025, value = 0.2)

                                            min_order = int(3.3*st.session_state.freq/(2*trans_width))
                                            max_order = int(max(1e5,min_order+1e3))
                                            order = st.number_input("Select Order:", min_value=min_order, max_value=max_order, value=min_order, step=2)

                                            st.session_state.Fir_filter = signal_processing.Fir_designer(st.session_state.freq,
                                                                                                         order,
                                                                                                         filter_selected,
                                                                                                         method,
                                                                                                         f_cut_l,
                                                                                                         f_cut_h,
                                                                                                         trans_width,
                                                                                                         window_selected = None,
                                                                                                         beta = None
                                                                                                         )

                                        case "Least Squares":

                                            trans_width = st.slider("Transition Width:", min_value = 0.1, max_value = f_cut_h - 0.025, value = 0.1)

                                            min_order = int(3.3*st.session_state.freq/(2*trans_width))
                                            max_order = int(max(1e5,min_order+1e3))
                                            order = st.number_input("Select Order:", min_value=min_order, max_value=max_order, value=min_order, step=2)                                            

                                            st.session_state.Fir_filter = signal_processing.Fir_designer(st.session_state.freq,
                                                                                                         order,
                                                                                                         filter_selected,
                                                                                                         method,
                                                                                                         f_cut_l,
                                                                                                         f_cut_h,
                                                                                                         trans_width,
                                                                                                         window_selected = None,
                                                                                                         beta = None
                                                                                                         )
                                            
                                case "Lowpass Filter":

                                    f_cut_l = st.slider("Cutoff frequency:", min_value= 10.0, max_value= 0.45*st.session_state.freq, value=30.0)
                                    f_cut_h = None

                                    match method:

                                        case "Window Method":                                    

                                            if window_selected == "Kaiser":

                                                trans_width = st.slider("Transition Width:", min_value = 0.05, max_value = (st.session_state.freq/2-f_cut_l)/2 - 0.1, step=0.05)

                                                beta = signal_processing.estimate_kaiser_beta(order, trans_width, st.session_state.freq)

                                                st.session_state.Fir_filter = signal_processing.Fir_designer(st.session_state.freq,
                                                                                                             order,
                                                                                                             filter_selected,
                                                                                                             method,
                                                                                                             f_cut_l,
                                                                                                             f_cut_h,
                                                                                                             window_selected,
                                                                                                             beta,
                                                                                                             trans_width
                                                                                                             )
                                                
                                            else:

                                                trans_width = None
                                                st.session_state.Fir_filter = signal_processing.Fir_designer(st.session_state.freq,
                                                                                                             order,
                                                                                                             filter_selected,
                                                                                                             method,
                                                                                                             f_cut_l,
                                                                                                             f_cut_h,
                                                                                                             trans_width,
                                                                                                             window_selected,
                                                                                                             beta = None,
                                                                                                             )

                                        case "Equiripple":

                                            #atten_cut = st.number_input("Attenuation in Cutoff Region:", min_value=0, max_value=1, value=0)
                                            #gain_pass = st.number_input("Gain in Pass Region:", min_value=1)
                                            trans_width = st.slider("Transition Width:", min_value = 0.2, max_value = (st.session_state.freq/2-f_cut_l)/2 - 0.1, step=0.2)

                                            min_order = int(3.3*st.session_state.freq/(2*trans_width))
                                            max_order = int(max(1e5,min_order+1e3))
                                            order = st.number_input("Select Order:", min_value=min_order, max_value=max_order, value=min_order, step=2)                                            

                                            st.session_state.Fir_filter = signal_processing.Fir_designer(st.session_state.freq,
                                                                                                         order,
                                                                                                         filter_selected,
                                                                                                         method,
                                                                                                         f_cut_l,
                                                                                                         f_cut_h,
                                                                                                         trans_width,
                                                                                                         window_selected = None,
                                                                                                         beta = None
                                                                                                         )

                                        case "Least Squares":

                                            trans_width = st.slider("Transition Width:", min_value = 0.1, max_value = (st.session_state.freq/2-f_cut_l)/2 - 0.1, step=0.1)
                                            
                                            min_order = int(3.3*st.session_state.freq/(2*trans_width))
                                            max_order = int(max(1e5,min_order+1e3))
                                            order = st.number_input("Select Order:", min_value=min_order, max_value=max_order, value=min_order, step=2)                                            

                                            st.session_state.Fir_filter = signal_processing.Fir_designer(st.session_state.freq,
                                                                                                         order,
                                                                                                         filter_selected,
                                                                                                         method,
                                                                                                         f_cut_l,
                                                                                                         f_cut_h,
                                                                                                         trans_width,
                                                                                                         window_selected = None,
                                                                                                         beta = None
                                                                                                         )

                                case "Bandpass Filter":

                                    band = st.radio("Select an EEG band:", [r'$\delta$ (0.5-3.5 Hz)', r'$\theta$ (4-7 Hz)', r'$\alpha$ (8-13 Hz)', r'$\beta$ (13-30 Hz)', r'$\gamma$ (>30 Hz)',  r'custom']) 

                                    f_pass1 = None
                                    f_pass2 = None

                                    if band == 'custom':
                                        column1, column2 = st.columns(2)
                                        with column1:

                                            f_pass1 = st.slider("Pass Band 1:", min_value= 1.0, max_value= 0.40*st.session_state.freq, value = 1.0)
                                            
                                        with column2: 

                                            f_pass2 = st.slider("Pass Band 2:", min_value= f_pass1 + 0.1, max_value= 0.45*st.session_state.freq, value= f_pass1 + 0.1)
 
                                    else:    
                                        match band:
                                    
                                            case r'$\delta$ (0.5-3.5 Hz)':
                    
                                                f_pass1 = 0.5
                                                f_pass2 = 3.5
                    
                                            case r'$\theta$ (4-7 Hz)':
                    
                                                f_pass1 = 4
                                                f_pass2 = 7
                                            
                                            case r'$\alpha$ (8-13 Hz)':
                    
                                                f_pass1 = 8
                                                f_pass2 = 13
                                            
                                            case r'$\beta$ (13-30 Hz)':
            
                                                f_pass1 =  13
                                                f_pass2 = 30
                                            
                                            case r'$\gamma$ (>30 Hz)':
                    
                                                f_pass1 = 30
                                                f_pass2 = 0.45*st.session_state.freq
                                                                                                                  
                                    match method:

                                        case "Window Method":
                                          
                                            if window_selected == "Kaiser":

                                                trans_width = st.slider("Transition Width:", min_value = 0.05, max_value = min(f_pass1,(st.session_state.freq/2-f_pass2)) - 0.1, value = 0.1)

                                                beta = signal_processing.estimate_kaiser_beta(order, trans_width,st.session_state.freq)

                                                st.session_state.Fir_filter = signal_processing.Fir_designer(st.session_state.freq,
                                                                                                                  order,
                                                                                                                  filter_selected,
                                                                                                                  method,
                                                                                                                  f_pass1,
                                                                                                                  f_pass2,
                                                                                                                  trans_width,
                                                                                                                  window_selected,
                                                                                                                  beta
                                                                                                                  )
                                                
                                            else:

                                                trans_width = None
                                                st.session_state.Fir_filter = signal_processing.Fir_designer(st.session_state.freq,
                                                                                                                  order,
                                                                                                                  filter_selected,
                                                                                                                  method,
                                                                                                                  f_pass1,
                                                                                                                  f_pass2,
                                                                                                                  trans_width,
                                                                                                                  window_selected,
                                                                                                                  beta = None
                                                                                                                  )

                                        case "Equiripple":

                                            trans_width = st.slider("Transition Width:", min_value = 0.2, max_value = min(f_pass1,(st.session_state.freq/2-f_pass2)) - 0.1, value = 0.2)

                                            min_order = int(3.3*st.session_state.freq/(2*trans_width))
                                            max_order = int(max(1e5,min_order+1e3))
                                            order = st.number_input("Select Order:", min_value=min_order, max_value=max_order, value=min_order, step=2)                                            
                                            st.session_state.Fir_filter = signal_processing.Fir_designer(st.session_state.freq,
                                                                                                         order,
                                                                                                         filter_selected,
                                                                                                         method,
                                                                                                         f_pass1,
                                                                                                         f_pass2,
                                                                                                         trans_width,
                                                                                                         window_selected = None,
                                                                                                         beta = None
                                                                                                         )

                                        case "Least Squares":  

                                            trans_width = st.slider("Transition Width:", min_value = 0.2, max_value = min(f_pass1,(st.session_state.freq/2-f_pass2)) - 0.1, value = 0.2)
                                               
                                            min_order = int(3.3*st.session_state.freq/(2*trans_width))
                                            max_order = int(max(1e5,min_order+1e3))
                                            order = st.number_input("Select Order:", min_value=min_order, max_value=max_order, value=min_order, step=2)                                            

                                            st.session_state.Fir_filter = signal_processing.Fir_designer(st.session_state.freq,
                                                                                                         order,
                                                                                                         filter_selected,
                                                                                                         method,
                                                                                                         f_pass1,
                                                                                                         f_pass2,
                                                                                                         trans_width,
                                                                                                         window_selected = None,
                                                                                                         beta = None
                                                                                                         )

                                case "Notch Filter":

                                    column1, column2 = st.columns(2)

                                    with column1:

                                        f_cut1 = st.slider("Stop Band 1:", min_value= 1.0, max_value = 0.40*st.session_state.freq, value = 1.0)
                                                                                
                                    with column2: 

                                        f_cut2 = st.slider("Stop Band 2:", min_value = f_cut1 + 0.1, max_value = 0.45*st.session_state.freq, value = f_cut1 + 0.1)
                                            
                                    match method:

                                        case "Window Method":
                                          
                                            if window_selected == "Kaiser":

                                                trans_width = st.slider("Transition WIdth:", min_value = 0.05, max_value = min(f_cut1, (st.session_state.freq/2 - f_cut2)) - 0.1, value = 0.1)

                                                beta = signal_processing.estimate_kaiser_beta(order, trans_width,st.session_state.freq)

                                                st.session_state.Fir_filter = signal_processing.Fir_designer(st.session_state.freq,
                                                                                                             order,
                                                                                                             filter_selected,
                                                                                                             method,
                                                                                                             f_cut1,
                                                                                                             f_cut2,
                                                                                                             trans_width,
                                                                                                             window_selected,
                                                                                                             beta
                                                                                                             )
                                                
                                            else:

                                                trans_width = None   
                                                st.session_state.Fir_filter = signal_processing.Fir_designer(st.session_state.freq,
                                                                                                             order,
                                                                                                             filter_selected,
                                                                                                             method,
                                                                                                             f_cut1,
                                                                                                             f_cut2,
                                                                                                             trans_width,
                                                                                                             window_selected,
                                                                                                             beta = None
                                                                                                             )

                                        case "Equiripple":

                                            trans_width = st.slider("Transition Width:", min_value = 0.2, max_value = min(f_cut1, (st.session_state.freq/2 - f_cut2)) - 0.1, value = 0.2)

                                            th_order = int(3.3*st.session_state.freq / (2*trans_width))

                                            SAFE_MAX_ORDER = 1500

                                            if th_order > SAFE_MAX_ORDER:
                                                st.warning(f"Equiripple can't converge over {SAFE_MAX_ORDER} Taps due to numerical limitations. Order has been limited. For {th_order} order transitions, use 'Window Method'." )
                                                min_order = SAFE_MAX_ORDER
                                            else: min_order = th_order

                                            order = st.number_input("Select Order:", min_value=2, max_value=SAFE_MAX_ORDER, value=min_order, step=2)  
                                         
                                            st.session_state.Fir_filter = signal_processing.Fir_designer(st.session_state.freq,
                                                                                                         order,
                                                                                                         filter_selected,
                                                                                                         method,
                                                                                                         f_cut1,
                                                                                                         f_cut2,
                                                                                                         trans_width,
                                                                                                         window_selected = None,
                                                                                                         beta = None
                                                                                                         )
                                            
                                        case "Least Squares":   

                                            trans_width = st.slider("Transition Width:", min_value = 0.1, max_value = min(f_cut1, (st.session_state.freq/2 - f_cut2)) - 0.1, value = 0.1)

                                            min_order = int(3.3*st.session_state.freq/(2*trans_width))
                                            max_order = int(max(1e5,min_order+1e3))
                                            order = st.number_input("Select Order:", min_value=min_order, max_value=max_order, value=min_order, step=2)                                            

                                            st.session_state.Fir_filter = signal_processing.Fir_designer(st.session_state.freq,
                                                                                                         order,
                                                                                                         filter_selected,
                                                                                                         method,
                                                                                                         f_cut1,
                                                                                                         f_cut2,
                                                                                                         trans_width,
                                                                                                         window_selected = None,
                                                                                                         beta = None
                                                                                                         )

                            st.write("Filter Frequency Response")
                            st.pyplot(display_filter(st.session_state.Fir_filter,
                                                     filter_selected, 
                                                     st.session_state.freq, 
                                                     len(st.session_state.data_processing)
                                                     )
                                      )

                            st.session_state.data_processing = signal_processing.Filter_data(st.session_state.data_processing,
                                                                                             st.session_state.Fir_filter
                                                                                             )


                            
                        except Exception as e:
                            st.error(f"An error occurred while filtering: {e}")

                    st.write("Filtered Signal")
                    st.pyplot(display_data(st.session_state.data_processing,
                                            st.session_state.channel_selected_name,
                                            st.session_state.time,
                                            st.session_state.freq,
                                            st.session_state.dimension_unit,
                                            state = "filtered"
                                            ),
                              use_container_width=True
                              )

    finally:

        if os.path.exists(temp_path):
            os.remove(temp_path)    
