# EEG Toolbox (v2.0)

**EEG Toolbox** is an interactive, open-source Graphical User Interface (GUI) built to make the analysis, filtering, and fast and intuitive visualization of electroencephalographic (EEG) signals. Developed as a dedicated Digital Signal Processing (DSP) tool, it allows students and researchers to explore neurophysiological data and design custom digital filters without requiring programming knowledge. 

With version 2.0, your entire analysis pipeline and plots can be automatically compiled and exported into a dynamically paginated, vector-graphics PDF report directly from the interface.

## Key Features & DSP Upgrades

This version introduces heavy architectural upgrades to the core signal processing engine and the data visualization pipeline:

* **Robust Data I/O**: Natively loads European Data Format (`.edf`) files, handling multi-channel arrays and utilizing memory-safe extraction protocols.
* **Signal Processing Pipeline**: Allows the user to perform Bad Channel Removal & Interpolation, Downsampling, and Re-Referencing through Common Average Referencing
* **Advanced Artifact Rejection**: Implements bad channel interpolation using Inverse Distance Weighting (IDW), Common Average Reference (CAR), and Independent Component Analysis (ICA) via FastICA for the isolation of ocular and muscular artifacts.
* **Optimized Powerline Artifact Removal**: The 50/60 Hz Notch filter has been migrated to an Infinite Impulse Response (IIR) architecture. This provides high computational efficiency and precise attenuation of AC interference without distorting adjacent frequency bands.
* **Advanced FIR Filter Design**: Comprehensive support for FIR filter synthesis using the **Window Method** (Hanning, Hamming, Blackman, Kaiser), the **Equiripple** (Parks-McClellan) algorithm, and **Least Squares** optimization.
* **Dynamic Safety Clamps & Order Routing**: Cutoff frequencies, transition widths, and filter orders are dynamically constrained based on the signal's Nyquist frequency and filter order. This provides more mathematical stability and prevents algorithmic non-convergence (e.g., within the Remez exchange algorithm).
* **Filter Comparison**: The filter option is presented with frequency respones of the FIR design options (Window, Equiripple, Least Squares). The user can tune the **order** and the **transition width** of every filter to finally select the best option for the signal processing.
* **Spectral Analysis**: Computes and visualizes the Power Spectral Density (PSD) using Welch's method across localized brain lobes for neurological frequency band inspection.
* **Jupyter Notebook**: Added a Jupyter Notebook demo of the program, giving a complete, automatic overview of the functions proposed. The experiment shown focuses on isolating the Theta band (3-7 Hz) from an EEG sample, showing the filtering options and choosing the best result.

## Architecture & Performance

The application is built on a Streamlit frontend strictly decoupled from the mathematical backend. To ensure real-time responsiveness even with large data arrays, the toolbox implements advanced caching strategies on computationally expensive nodes (e.g., forward-backward convolution, filter synthesis, and ICA), optimizing the trade-off between CPU load and RAM saturation.

## Installation & Usage

### Option 1: Standalone Application (.exe)

If you do not have Python installed, you can run the pre-compiled version:
1. Navigate to the **Releases** tab on the right side of this repository.
2. Download the latest `.zip` archive.
3. Extract the entire folder to your local machine (do not run it directly from inside the `.zip`).
4. In the `EEG_Toolbox` folder, run `EEG_Toolbox.exe`.

**Note on Antivirus**
Because this is an unsigned executable generated via `PyInstaller`, Windows Defender SmartScreen may flag it as an unrecognized application (False Positive). Click **"More Info" -> "Run anyway"**.

### Option 2: Python Source Code (Developers)

To run the Toolbox locally from the source code:

```bash
git clone [https://github.com/dmasciola/EEG_Toolbox.git](https://github.com/dmasciola/EEG_Toolbox.git)
cd EEG_Toolbox
pip install -r requirements.txt
streamlit run app.py
```
## Feeback and Contributions

This project is under active development. Any feedback regarding bugs, usability improvements, or suggestions for implementing new DSP algorithms is highly appreciated. Feel free to open an **Issue** or submit a **Pull Request**.

Davide Masciola