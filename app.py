import streamlit as st
import tempfile
import os
from data_loader import load_edf_data
from data_displayer import display_data, display_filter
import signal_processing

def main():
    # --- SIDEBAR & SESSION RESET ---
    with st.sidebar:
        if st.button("Reset Toolbox", type="primary"):
            st.session_state.clear()
            st.rerun()

    # --- MAIN HEADER ---
    st.title("EEG Toolbox")
    st.caption("Developed by Davide Masciola | v1.0-beta")

    # --- STATE INITIALIZATION ---
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    if 'freq' not in st.session_state:
        st.session_state.freq = 1.0  # Safe default to prevent division by zero during init

    # --- FILE UPLOAD (Early Exit Pattern) ---
    uploaded_file = st.file_uploader("Upload EEG file", type=['edf'])
    
    if uploaded_file is None:
        st.info("Please upload an EDF file to begin analysis.")
        st.stop()  # Halts execution here, flattening the rest of the code

    # --- FILE HANDLING ---
    with tempfile.NamedTemporaryFile(delete=False, suffix='.edf') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        temp_path = tmp_file.name

    try:
        # Only extract if not already loaded to save computational time on reruns
        if not st.session_state.data_loaded:
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
                    
                    st.success("Data extracted successfully!")
                except Exception as e:
                    st.error(f"An error occurred during loading: {e}")
                    st.stop()

        # --- DATA OVERVIEW ---
        st.text("--- DATA EXTRACTER ---")
        st.text(f"Sampling frequency: {st.session_state.freq} Hz")
        st.text(f"Sampling time: {st.session_state.time} s")
        st.text(f"Channels: {st.session_state.n_channels}")
        st.text(f"Channel names: {st.session_state.channel_names[:]}")

        # --- CHANNEL SELECTION ---
        temp_channel = st.number_input(
            f"\nPlease select one channel to display (1 to {st.session_state.n_channels}):",
            min_value=1, 
            max_value=st.session_state.n_channels, 
            value=1
        )

        if st.button("Load Channel"):
            st.session_state.channel_selected = temp_channel
            st.session_state.data_selected = st.session_state.data_matrix[st.session_state.channel_selected - 1, :]
            st.session_state.channel_selected_name = st.session_state.channel_names[st.session_state.channel_selected - 1]
            st.success(f"Channel {st.session_state.channel_selected} loaded successfully")

        # Wait until a channel is actually selected before proceeding
        if 'channel_selected' not in st.session_state:
            st.stop()

        # --- ORIGINAL SIGNAL PLOT ---
        st.write("### Original Signal")
        fig_original = display_data(
            st.session_state.data_selected,
            st.session_state.channel_selected_name,
            st.session_state.time,
            st.session_state.freq,
            st.session_state.dimension_unit,
            state="default"
        )
        st.pyplot(fig_original, use_container_width=True)

        st.divider()
        
        # --- SIGNAL PROCESSING SECTION ---
        st.write("### Signal Processing")
        st.write("Please select an option")

        # Reset processing array
        st.session_state.data_processing = st.session_state.data_selected.copy()
        st.session_state.Fir_filter = None
        
        # 1. NOTCH FILTERING
        if st.checkbox("1. Current Artifact Remover"):
            current_state = st.radio("Select Continent:", ['America (60 Hz)', 'Europe (50 Hz)'], index=None)    
            
            if current_state:
                f_current = 60 if current_state == 'America (60 Hz)' else 50
                Q = st.slider("Q-factor:", min_value=f_current, max_value=f_current*100, value=f_current*10)                            
                
                st.session_state.data_processing = signal_processing.Current_Remover(
                    st.session_state.data_processing,
                    st.session_state.freq,
                    f_current,
                    Q
                )

        # 2. FIR FILTERING
        if st.checkbox("2. Filter"):
            filter_selected = st.radio("Select Filter:", ["Highpass Filter", "Lowpass Filter", "Bandpass Filter", "Notch Filter"])
            method = st.radio("Filtering method:", ["Window Method", "Equiripple", "Least Squares"])
            
            # Initialize default routing variables to prevent UnboundLocalError
            f_cut_l, f_cut_h = 0.0, 0.0
            trans_width = 0.0
            window_selected = ""
            beta = 0.0
            order = 201

            # --- DYNAMIC PARAMETER GATHERING ---
            if method == "Window Method":
                window_selected = st.radio("Window:", ["Hanning", "Hamming", "Blackman", "Kaiser"])
                if window_selected != "Kaiser":
                    order_method = st.radio("Filter Order:", ["Manual", "Auto"])
                    if order_method == "Auto":
                        factors = {"Hanning": 3.1, "Hamming": 3.3, "Blackman": 5.5}
                        factor = factors.get(window_selected, 3.3)
                        order = int(2 * factor * st.session_state.freq)
                    else:
                        order = st.number_input("Select Order:", min_value=2, max_value=int(1e4), value=201, step=2)
                else:
                    order = st.number_input("Select Order:", min_value=2, max_value=int(1e4), value=201, step=2)

            # Frequency Limits & Transitions based on Topology
            try:
                nyquist = 0.5 * st.session_state.freq
                
                if filter_selected == "Highpass Filter":
                    f_cut_h = st.slider("Cutoff frequency (Hz):", min_value=0.5, max_value=0.45*st.session_state.freq, value=0.5)
                    if method in ["Equiripple", "Least Squares"]:
                        trans_width = st.slider("Transition Width (Hz):", min_value=0.1, max_value=f_cut_h - 0.025, value=0.2)
                    elif window_selected == "Kaiser":
                        trans_width = st.slider("Transition Width (Hz):", min_value=0.05, max_value=f_cut_h - 0.025, value=0.05)
                        beta = signal_processing.estimate_kaiser_beta(order, trans_width, st.session_state.freq)

                elif filter_selected == "Lowpass Filter":
                    f_cut_l = st.slider("Cutoff frequency (Hz):", min_value=10.0, max_value=0.45*st.session_state.freq, value=30.0)
                    if method in ["Equiripple", "Least Squares"]:
                        trans_width = st.slider("Transition Width (Hz):", min_value=0.1, max_value=(nyquist-f_cut_l)/2 - 0.1, step=0.2, value=0.2)
                    elif window_selected == "Kaiser":
                        trans_width = st.slider("Transition Width (Hz):", min_value=0.05, max_value=(nyquist-f_cut_l)/2 - 0.1, step=0.05, value=0.1)
                        beta = signal_processing.estimate_kaiser_beta(order, trans_width, st.session_state.freq)

                elif filter_selected in ["Bandpass Filter", "Notch Filter"]:
                    if filter_selected == "Bandpass Filter":
                        band = st.radio("Select an EEG band:", [r'$\delta$ (0.5-3.5 Hz)', r'$\theta$ (4-7 Hz)', r'$\alpha$ (8-13 Hz)', r'$\beta$ (13-30 Hz)', r'$\gamma$ (>30 Hz)', 'custom'])
                        if band == 'custom':
                            col1, col2 = st.columns(2)
                            with col1: f_cut_l = st.slider("Pass Band 1 (Hz):", min_value=1.0, max_value=0.40*st.session_state.freq, value=1.0)
                            with col2: f_cut_h = st.slider("Pass Band 2 (Hz):", min_value=f_cut_l + 0.1, max_value=0.45*st.session_state.freq, value=f_cut_l + 0.1)
                        else:
                            bands_map = {
                                r'$\delta$ (0.5-3.5 Hz)': (0.5, 3.5),
                                r'$\theta$ (4-7 Hz)': (4.0, 7.0),
                                r'$\alpha$ (8-13 Hz)': (8.0, 13.0),
                                r'$\beta$ (13-30 Hz)': (13.0, 30.0),
                                r'$\gamma$ (>30 Hz)': (30.0, 0.45*st.session_state.freq)
                            }
                            f_cut_l, f_cut_h = bands_map[band]
                    else:
                        col1, col2 = st.columns(2)
                        with col1: f_cut_l = st.slider("Stop Band 1 (Hz):", min_value=1.0, max_value=0.40*st.session_state.freq, value=1.0)
                        with col2: f_cut_h = st.slider("Stop Band 2 (Hz):", min_value=f_cut_l + 0.1, max_value=0.45*st.session_state.freq, value=f_cut_l + 0.1)

                    if method in ["Equiripple", "Least Squares"]:
                        trans_width = st.slider("Transition Width (Hz):", min_value=0.1, max_value=min(f_cut_l, (nyquist - f_cut_h)) - 0.1, value=0.2)
                    elif window_selected == "Kaiser":
                        trans_width = st.slider("Transition Width (Hz):", min_value=0.05, max_value=min(f_cut_l, (nyquist - f_cut_h)) - 0.1, value=0.1)
                        beta = signal_processing.estimate_kaiser_beta(order, trans_width, st.session_state.freq)

                # Advanced Order Calculation for Equiripple/Least Squares
                if method in ["Equiripple", "Least Squares"]:
                    min_order = int(3.3 * st.session_state.freq / (2 * trans_width))
                    SAFE_MAX_ORDER = 1500 if method == "Equiripple" else int(max(2e3, min_order + 5e2))
                    
                    if method == "Equiripple" and min_order > SAFE_MAX_ORDER:
                        st.warning(f"Equiripple cannot converge over {SAFE_MAX_ORDER} taps due to numerical limitations. Order has been capped. For {min_order}-order transitions, use the 'Window Method'.")
                        min_order = SAFE_MAX_ORDER
                        
                    order = st.number_input("Select Order:", min_value=2, max_value=SAFE_MAX_ORDER, value=min_order, step=2)

                # --- UNIFIED FILTER EXECUTION ---
                st.session_state.Fir_filter = signal_processing.Fir_designer(
                    frequency=st.session_state.freq,
                    order=order,
                    filter_selected=filter_selected,
                    method=method,
                    f_cut_low=f_cut_l,
                    f_cut_high=f_cut_h,
                    trans_width=trans_width,
                    window_selected=window_selected,
                    beta=beta
                )

                # --- BODE PLOT RENDER ---
                st.write("### Filter Frequency Response")
                fig_filter = display_filter(
                    st.session_state.Fir_filter,
                    filter_selected, 
                    st.session_state.freq
                )
                st.pyplot(fig_filter)

                # --- APPLY FILTER ---
                st.session_state.data_processing = signal_processing.Filter_data(
                    st.session_state.data_processing,
                    st.session_state.Fir_filter
                )

            except Exception as e:
                st.error(f"An error occurred while computing the filter: {e}")

        # --- FILTERED SIGNAL PLOT ---
        st.write("### Filtered Signal")
        fig_filtered = display_data(
            st.session_state.data_processing,
            st.session_state.channel_selected_name,
            st.session_state.time,
            st.session_state.freq,
            st.session_state.dimension_unit,
            state="filtered"
        )
        st.pyplot(fig_filtered, use_container_width=True)

    finally:
        # Ensures the temporary file is deleted from system memory after execution completes
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except PermissionError:
                pass # Prevents crashes if Windows hasn't fully released the file lock yet

if __name__ == "__main__":
    main()