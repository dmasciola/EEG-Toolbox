import os
import sys
import streamlit.web.cli as stcli

import pyedflib
from scipy import fft, signal
import matplotlib.pyplot
import numpy

if __name__ == "__main__":
    # temporary file extraction in MEIPASS
    if getattr(sys, 'frozen', False):
        dirname = sys._MEIPASS
    else:
        dirname = os.path.dirname(__file__)
        
    # Change 'app.py' if the file is named differently
    app_path = os.path.join(dirname, 'app.py') 
    
    # emulate "streamlit run app.py"
    sys.argv = ["streamlit", "run", app_path, "--global.developmentMode=false"]
    sys.exit(stcli.main())