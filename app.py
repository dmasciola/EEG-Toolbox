import streamlit as st
import tempfile
import os
from data_loader import load_edf_data
import data_displayer as disp
import signal_processing
import montages
from numpy import linspace


st.set_page_config(
    page_title="EEG Toolbox",
    layout="wide", 
    initial_sidebar_state="collapsed"
)

report_log = {}

def main():
    # --- SIDEBAR & SESSION RESET ---
    with st.sidebar:
        if st.button("Reset Toolbox", type="primary"):
            st.session_state.clear()
            st.rerun()

    # --- MAIN HEADER ---
    st.title("EEG Toolbox")
    st.caption("Developed by Davide Masciola | v2.0")

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
                    st.session_state.electrode_layout = montages.get_layout(n_channels)
                    
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
        report_log['Data Loaded'] = f"Loaded {uploaded_file.name} with {st.session_state.n_channels} channels at {st.session_state.freq} Hz for {st.session_state.time:.2f} seconds."
        st.divider()

        # --- TOPOGRAPHIC MAP ---
        if st.session_state.electrode_layout is not None:
            st.write("### Electrode Topography")

            fig_topomap = disp.scalp_map(st.session_state.electrode_layout)

            _, col_topomap, _ = st.columns([1, 2, 1])
            with col_topomap:
                st.pyplot(fig_topomap, use_container_width=False)

        st.divider()

        # --- DATA PLOTTING ---
        st.write("### Raw Data Plotting")

        st.session_state.time_width = st.number_input(
            "Select Time Window (s):", 
            min_value=1, 
            max_value=20, 
            value=10
        )

        st.session_state.time_start = st.slider("Select Time Start(s):", min_value=0.0, max_value=st.session_state.time - st.session_state.time_width, value=0.0, step=0.1)
        fig_original = disp.displayer(st.session_state.data_matrix, st.session_state.time_start, st.session_state.time_width, st.session_state.channel_names, st.session_state.freq, st.session_state.dimension_unit)
        st.pyplot(fig_original, use_container_width=True)

        # --- CHANNEL INSPECTION ---
        st.write("### Channel Inspection")
        st.session_state.channel_selected = st.selectbox(
            f"\nPlease select the channel to inspect:",
            options=st.session_state.channel_names,
            index = 0
        )

        selected_channel_index = st.session_state.channel_names.index(st.session_state.channel_selected)
        st.session_state.data_selected = st.session_state.data_matrix[selected_channel_index, :]
        st.session_state.channel_selected_name = st.session_state.channel_names[selected_channel_index]

        # --- DATA INSPECTION PLOT ---
        fig_inspect = disp.display_data(
            st.session_state.data_selected,
            st.session_state.channel_selected_name,
            st.session_state.time,
            st.session_state.freq,
            st.session_state.dimension_unit,
        )
        st.pyplot(fig_inspect, use_container_width=True)

        st.divider()

        
        # Reset processing array
        st.session_state.data_processing = st.session_state.data_matrix.copy()
        st.session_state.Fir_filter = None


        # --- DATA PROCESSING SECTION ---
        st.write("### Data Processing")
        st.write("Please select an option")


        # 1. BAD CHANNEL REMOVAL

        if st.checkbox("1. Bad Channel Removal & Interpolation"):
            bad_channels = st.multiselect(
                "Select bad channels to remove:",
                options=st.session_state.channel_names,
                default=[]
            )

            if bad_channels:
                st.session_state.data_processing = signal_processing.Remove_bad_channels(
                    st.session_state.data_processing,
                    [st.session_state.channel_names.index(ch) for ch in bad_channels]
                )
                st.success(f"Removed channels: {', '.join(bad_channels)}")
                st.session_state.data_processing = signal_processing.Interpolate_bad_channels(
                    st.session_state.data_processing,
                    st.session_state.channel_names,
                    [st.session_state.channel_names.index(ch) for ch in bad_channels],
                    st.session_state.electrode_layout
                )

                report_log['Bad Channels Removed'] = f"Removed and Interpolated channels: {', '.join(bad_channels)}."

            else:
                st.info("No channels selected for removal.")

        # 2. DOWNSAMPLING

        current_freq = st.session_state.freq
        if st.checkbox("2. Downsample Data"):
            downsample_factor = st.slider(
                "Select downsampling factor:",
                min_value=1,
                max_value=10,
                value=1
            )

            if downsample_factor > 1:
                st.session_state.data_processing = signal_processing.Downsample(
                    st.session_state.data_processing,
                    downsample_factor
                )
                current_freq = st.session_state.freq / downsample_factor
                st.success(f"Data downsampled by a factor of {downsample_factor}. New frequency: {current_freq} Hz")

                report_log['Downsampling'] = f"Data downsampled by a factor of {downsample_factor}. New frequency: {current_freq} Hz."

            else:
                st.info("Downsampling factor is 1, no downsampling applied.")

        # 3. RE-REFERENCING

        if st.checkbox("3. Re-reference Data"):
            st.session_state.data_processing = signal_processing.Common_average_reference(
                st.session_state.data_processing
            )

            report_log['Re-referencing'] = "Data re-referenced using Common Average Reference (CAR)."

        # 4. CURRENT ARTIFACT REMOVAL

        if st.checkbox("4. Current Artifact Remover"):
            current_state = st.radio("Select Continent:", ['America (60 Hz)', 'Europe (50 Hz)'], index=None)    
        
            if current_state:
                f_current = 60 if current_state == 'America (60 Hz)' else 50
                Q = st.slider("Q-factor:", min_value=f_current, max_value=int(1e3), value=f_current*10)                            
            
                st.session_state.data_processing = signal_processing.Current_Remover(
                    st.session_state.data_processing,
                    current_freq,
                    f_current,
                    Q
                )
                report_log['Current Artifact Removal'] = f"Applied current artifact removal with {f_current} Hz notch filter and Q-factor: {Q}."

        # 5. INDEPENDENT COMPONENT ANALYSIS (ICA)

        if st.checkbox("5. Independent Component Analysis (ICA)"):
            n_components = st.slider("Number of Components:", min_value=1, max_value=20, value=5)

            S_, A_, data_mean = signal_processing.Compute_ICA(st.session_state.data_processing, n_components)
            freq_PSD, PSD_components = signal_processing.Compute_PSD(S_, current_freq)
            fig_components = disp.show_components(S_, freq_PSD, PSD_components, current_freq, st.session_state.dimension_unit)
            st.pyplot(fig_components, use_container_width=True)

            bad_components = st.multiselect(
                "Select bad components to remove:",
                options=list(linspace(1, n_components, n_components, dtype=int)),
                default=[]
            )

            st.session_state.data_processing = signal_processing.Reconstruct_from_ICA(S_, A_, data_mean, bad_components)    

            report_log['ICA'] = f"Applied Independent Component Analysis through Welch Method, isolated {n_components} independent components, removed components: {', '.join(map(str, bad_components))}."

        # 6. FILTERING
        
        if st.checkbox("6. Filter"):
            filter_selected = st.radio("Select Filter:", ["Highpass Filter", "Lowpass Filter", "Bandpass Filter", "Notch Filter"])
            
            # Initialize default routing variables to prevent UnboundLocalError
            f_cut_l, f_cut_h = 0.0, 0.0
            trans_width = 0.0
            window_selected = ""
            beta = 0.0
            order = 201

            window_selected = st.radio("Window Method:", ["Hanning", "Hamming", "Blackman", "Kaiser"])
            factors = {"Hanning": 3.1, "Hamming": 3.3, "Blackman": 5.5}
            factor = factors.get(window_selected, 3.3)

            methods = ["Window Method", "Equiripple", "Least Squares"]

            st.session_state.Fir_filter = None

            # Frequency Limits based on Topology
            try:
                nyquist = 0.5 * current_freq
                
                if filter_selected == "Highpass Filter":
                    f_cut_h = st.slider("Cutoff frequency (Hz):", min_value=0.5, max_value=0.45*current_freq, value=0.5)

                    max_trans_width = f_cut_h - 0.025   #maximum transition width based on filter stability, defined for every filter type

                elif filter_selected == "Lowpass Filter":
                    f_cut_l = st.slider("Cutoff frequency (Hz):", min_value=10.0, max_value=0.45*current_freq, value=30.0)

                    max_trans_width = (nyquist-f_cut_l)/2 - 0.1    

                elif filter_selected in ["Bandpass Filter", "Notch Filter"]:
                    if filter_selected == "Bandpass Filter":
                        band = st.radio("Select an EEG band:", [r'$\delta$ (0.5-3.5 Hz)', r'$\theta$ (4-7 Hz)', r'$\alpha$ (8-13 Hz)', r'$\beta$ (13-30 Hz)', r'$\gamma$ (>30 Hz)', 'custom'])
                        if band == 'custom':
                            col_band_l, col_band_h = st.columns(2)
                            with col_band_l: f_cut_l = st.slider("Pass Band 1 (Hz):", min_value=1.0, max_value=0.40*current_freq, value=1.0)
                            with col_band_h: f_cut_h = st.slider("Pass Band 2 (Hz):", min_value=f_cut_l + 0.1, max_value=0.45*current_freq, value=f_cut_l + 0.1)
                        else:
                            #commonly used EEG band-maps
                            bands_map = {
                                r'$\delta$ (0.5-3.5 Hz)': (0.5, 3.5),
                                r'$\theta$ (4-7 Hz)': (4.0, 7.0),
                                r'$\alpha$ (8-13 Hz)': (8.0, 13.0),
                                r'$\beta$ (13-30 Hz)': (13.0, 30.0),
                                r'$\gamma$ (>30 Hz)': (30.0, 0.45*current_freq)
                            }
                            f_cut_l, f_cut_h = bands_map[band]
                            
                    else:
                        #allows the user to define a custom band
                        col_band_l, col_band_h = st.columns(2)
                        with col_band_l: f_cut_l = st.slider("Stop Band 1 (Hz):", min_value=1.0, max_value=0.40*current_freq, value=1.0)
                        with col_band_h: f_cut_h = st.slider("Stop Band 2 (Hz):", min_value=f_cut_l + 0.1, max_value=0.45*current_freq, value=f_cut_l + 0.1)

                    max_trans_width = min(f_cut_l, (nyquist - f_cut_h)) - 0.1   #here the trans_width is defined once since the filters are equal in structure

                # --- FILTER TUNING PARAMETERS ---
                
                col_trans_width_win, col_trans_width_eqr, col_trans_width_lsq = st.columns(3)
                with col_trans_width_win: trans_width_win = st.slider("Transition Width Window Method (Hz):", min_value=0.05, max_value=max_trans_width, value=0.2)
                with col_trans_width_eqr: trans_width_eqr = st.slider("Transition Width Equiripple (Hz):", min_value=0.1, max_value=max_trans_width, value=0.2)
                with col_trans_width_lsq: trans_width_lsq = st.slider("Transition Width Least Squares (Hz)", min_value=0.1, max_value=max_trans_width, value=0.2)
                    
                min_order_win= int(2 * factor * current_freq)
                SAFE_MAX_ORDER_EQR = 1500
                min_order_eqr = int(3.3 * current_freq / (2 * trans_width_eqr))
                min_order_lsq = int(3.3 * current_freq / (2 * trans_width_lsq))
                max_order = int(5e3)

                col_order_win, col_order_eqr, col_order_lsq = st.columns(3)
                with col_order_win: order_win= st.number_input("Window order:", min_value=min_order_win, max_value=max_order, value=min_order_win)

                if min_order_eqr > SAFE_MAX_ORDER_EQR:
                    st.warning(f"Equiripple cannot converge over {SAFE_MAX_ORDER_EQR} taps due to numerical limitations. Order has been capped. For {min_order_eqr}-order transitions, use the 'Window Method'.")
                    order_eqr = SAFE_MAX_ORDER_EQR                
                else:
                    with col_order_eqr: order_eqr = st.number_input("Equiripple order:", min_value=min_order_eqr, max_value=SAFE_MAX_ORDER_EQR, value=min_order_eqr)

                with col_order_lsq: order_lsq = st.number_input("Least Squares order:", min_value=min_order_lsq, max_value=max_order, value=min_order_lsq)   

                # --- FILTERS DESIGN ---

                if window_selected == "Kaiser":
                    beta = signal_processing.estimate_kaiser_beta(order_win, trans_width, current_freq)
                    Fir_window = signal_processing.Fir_designer(current_freq, order_win, filter_selected, methods[0], f_cut_l, f_cut_h, trans_width_win, window_selected, beta)

                else:
                    Fir_window = signal_processing.Fir_designer(current_freq, order_win, filter_selected, methods[0], f_cut_l, f_cut_h, trans_width_win, window_selected, beta=None)
                    
                Fir_equiripple = signal_processing.Fir_designer(current_freq, order_eqr, filter_selected, methods[1], f_cut_l, f_cut_h, trans_width_eqr, window_selected=None, beta=None)
                Fir_leastsquares = signal_processing.Fir_designer(current_freq, order_lsq, filter_selected, methods[2], f_cut_l, f_cut_h, trans_width_lsq, window_selected=None, beta=None)

                # --- FILTER PLOTTING ---

                fig_Fir_compared = disp.compare_filter(Fir_window, Fir_equiripple, Fir_leastsquares, filter_selected, current_freq)
                st.pyplot(fig_Fir_compared)

                # ----- USER CHOICE -----

                method_selected = st.radio("Select a FIR Filter:", ["Window Method", "Equiripple", "Least Squares"], index = None)

                if method_selected:
                    match method_selected:
                        case "Window Method":
                            st.session_state.Fir_filter = Fir_window
                            report_log['Filtering'] = f"Applied {filter_selected} FIR filter with order: {order_win}; method: {window_selected} Window; cutoff frequencies: {f_cut_l} Hz, {f_cut_h} Hz, with transition width: {trans_width_win} Hz."
                            
                        case "Equiripple":
                            st.session_state.Fir_filter = Fir_equiripple
                            report_log['Filtering'] = f"Applied {filter_selected} FIR filter with order: {order_eqr}; method: Equiripple; cutoff frequencies: {f_cut_l} Hz, {f_cut_h} Hz, with transition width: {trans_width_eqr} Hz."

                        case "Least Squares":
                            st.session_state.Fir_filter = Fir_leastsquares
                            report_log['Filtering'] = f"Applied {filter_selected} FIR filter with order: {order_lsq}; method: Least Squares; cutoff frequencies: {f_cut_l} Hz, {f_cut_h} Hz, with transition width: {trans_width_lsq} Hz."
                    
                if st.session_state.Fir_filter is not None:
                # --- APPLY FILTER ---
                    st.session_state.data_processing = signal_processing.Filter_data(
                        st.session_state.data_processing,
                        st.session_state.Fir_filter
                    )

                     
                      
            except Exception as e:
                st.error(f"An error occurred while computing the filter: {e}")



        # --- FILTERED SIGNAL PLOT ---
        st.divider()
        st.write("### Processed Data Plotting")
        if st.checkbox("Show Processed Data"):
            fig_filtered = disp.displayer(
                st.session_state.data_processing,
                st.session_state.time_start,
                st.session_state.time_width,
                st.session_state.channel_names,
                current_freq,
                st.session_state.dimension_unit
                )
            st.pyplot(fig_filtered, use_container_width=True)

        st.divider()

        # 7. SPECTRAL ANALYSIS
        st.write("### Spectral Analysis")
        if st.checkbox("Power Spectral Density (PSD) Analysis"):
            freq_PSD, PSD_data = signal_processing.Compute_PSD(st.session_state.data_processing, current_freq)
            fig_PSD = disp.display_PSD(freq_PSD, PSD_data, st.session_state.channel_names)
            st.pyplot(fig_PSD, use_container_width=True)

            report_log['PSD'] = f"Analyzed Power Spectral Density of the signal."

        # --- EXPORT REPORT ---
        st.divider()
        st.write("### Export Report")
        
        exported_figures = {}
        
        # Safely extract only the figures instantiated during the current session
        if 'fig_topomap' in locals(): exported_figures["Electrode Topography"] = fig_topomap
        if 'fig_original' in locals(): exported_figures["Raw Signal Overview"] = fig_original
        if 'fig_filtered' in locals(): exported_figures["Processed Signal"] = fig_filtered
        if 'fig_PSD' in locals(): exported_figures["Power Spectral Density"] = fig_PSD

        from pdf_exporter import generate_pdf
        
        pdf_bytes = generate_pdf(report_log, exported_figures)
        
        st.download_button(
            label="Download Clinical Report (.pdf)",
            data=pdf_bytes,
            file_name="EEG_Analysis_Report.pdf",
            mime="application/pdf",
            type="primary"
        )
    finally:
        # Ensures the temporary file is deleted from system memory after execution completes
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except PermissionError:
                pass # Prevents crashes if Windows hasn't fully released the file lock yet

#runs if the file is called
if __name__ == "__main__":
    main()