# EEG Toolbox (v1.0-beta)



**EEG Toolbox** is an interactive, open-source Graphical User Interface (GUI) built to make the analysis, filtering, and visualization of electroencephalographic (EEG) signals fast, intuitive, and mathematically rigorous. 



Developed as a dedicated Digital Signal Processing (DSP) tool, it allows students and researchers to explore neurophysiological data and design custom digital filters without requiring programming knowledge. Your analysis and plots can be easily exported using the "PRINT" function in the top right corner of the application.





### Key Features \& DSP Upgrades



This beta version introduces heavy architectural upgrades to the core signal processing engine:



* **Optimized Powerline Artifact Removal**: The 50/60 Hz Notch filter has been migrated to an Infinite Impulse Response (IIR) architecture. This guarantees high computational efficiency and surgical attenuation of AC interference without distorting adjacent frequency bands.
* **Advanced FIR Filter Design**: Comprehensive support for FIR filter synthesis using the **Window Method** (Hanning, Hamming, Blackman, Kaiser), the **Equiripple** (Parks-McClellan) algorithm, and **Least Squares** optimization.
* **Dynamic Safety Clamps \& Order Routing**: Cutoff frequencies, transition widths, and filter orders are dynamically constrained in real-time based on the signal's Nyquist frequency. This forces absolute mathematical stability and prevents algorithmic non-convergence (e.g., within the Remez exchange algorithm).





### Installation \& Usage



**Option 1**: Standalone Application (.exe)

If you do not have Python installed, you can run the pre-compiled version:

1. Navigate to the **Releases** tab on the right side of this repository.
2. Download the latest `.zip` archive.
3. Extract the entire folder to your local machine (do not run it directly from inside the `.zip`).
4. Run `EEG\_Toolbox.exe`. 



##### Note on Antivirus



Because this is an unsigned executable generated via `PyInstaller`, Windows Defender SmartScreen may flag it as an unrecognized application (False Positive). Click **"More Info" -> "Run anyway"**.



**Option 2**: Python Source Code (Developers)

To run the Toolbox locally from the source code:

```bash

git clone \[https://github.com/dmasciola/EEG\_Toolbox.git](https://github.com/dmasciola/EEG\_Toolbox.git)

cd EEG\_Toolbox

pip install -r requirements.txt

streamlit run app.py

```





### Feedback \& Contributions



This project is under active development. Any feedback regarding bugs, usability improvements, or suggestions for implementing new DSP algorithms is highly appreciated. Feel free to open an **Issue** or submit a **Pull Request**.





