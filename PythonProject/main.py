# Load NeuroKit and other useful packages
import neurokit2 as nk
import pandas as pd
import numpy as np
import time
import os
import keyboard

# Save File locations into string
ecg_csv= "bioharness/bin/Debug/netcoreapp3.1/Experiment/Session/ecgLog.csv"
rsp_csv= "bioharness/bin/Debug/netcoreapp3.1/Experiment/Session/breathingLog.csv"

def process_ecg(data):
    ecg_activity = data.iloc[:, 0]
    ecg_timestamp = round(data.iloc[:, 1], 2) # Round time to two dp
    ecg_entries = ecg_activity[100:] # Change number to match entries made every 5 seconds
    
    # Processing ECG data
    ecg = nk.ecg_process(ecg_entries, sampling_rate=100)  # Fix sampling rate later
    ecg_cleaned = nk.ecg_clean(ecg, sampling_rate=100)
    ecg_peaks= nk.ecg_peaks(ecg_cleaned, sampling_rate=100)
    
    # Get RMSSD of all entries
    hrv_time = nk.hrv_time(ecg_peaks, sampling_rate=100, show = True)
    rmssd = hrv_time['RMSSD']
    
    # Creating Dataframes
    ecg_dataframe = pd.DataFrame({'HRV RMSSD': rmssd,
                                  'HRV RMSSD Timestamp': ecg_timestamp})
    return ecg_dataframe
    
def process_rsp(data):
    rsp_rate = data.iloc[:, 0]
    rsp_timestamp = round(data.iloc[:, 1], 2) # Round time to two dp
    rsp_entries = rsp_rate[100:] # Change number to match entries made every 5 seconds
    
    rsp = nk.rsp_process(rsp_entries, sampling_rate=100) # Fix sampling rate later
    rsp_cleaned = nk.rsp_clean(rsp, sampling_rate=100)
    rsp_amplitude = nk.rsp_amplitude(rsp_cleaned, sampling_rate = 100)
    rsp_peaks = nk.rsp_findpeaks(rsp_cleaned, sampling_rate=100)
    rsp_rmssd = nk.rsp_rav(rsp_amplitude, rsp_peaks)
    
    # Creating Dataframes
    rsp_dataframe = pd.DataFrame({'RSP RMSSD': rsp_rmssd, 
                                  'RSP RMSSD Timestamp' : rsp_timestamp})
    return rsp_dataframe

os.makedirs('/output', exist_ok=True)

while(True):
    # while running, wait 5 seconds before running everything
    time.sleep(5)
    
    # Reads csv files and collects the ecg activity and timestamp in own location
    ecg_data = pd.read_csv(ecg_csv)
    rsp_data = pd.read_csv(rsp_csv)
    
    # Process data and save to dataframes
    ecg_dataframe = process_ecg(ecg_data)
    rsp_dataframe = process_rsp(rsp_data)
    
    # Save to seperate csv files
    ecg_dataframe.to_csv("/output/ecg_output.csv")
    rsp_dataframe.to_csv("/output/rsp_output.csv")
    
    # If key is pressed, quit program
    if keyboard.is_pressed('P'):
        ecg_dataframe.to_csv("/output/ecg_output.csv")
        rsp_dataframe.to_csv("/output/rsp_output.csv")
        exit(0)
