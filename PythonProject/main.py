# Load NeuroKit and other useful packages
import neurokit2 as nk
import pandas as pd
import numpy as np
import seaborn as sb
import time


while(True):
    time.sleep(1)
    ecg_data = pd.read_csv('logs\ecgLog.csv')
    ecg_activity = ecg_data.iloc[:, 0]
    ecg_timestamp = ecg_data.iloc[:, 1]
    print(ecg_activity[5:])
        