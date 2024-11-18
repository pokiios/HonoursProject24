# Load NeuroKit and other useful packages
import neurokit2 as nk
import pandas as pd
import numpy as np
import os
import keyboard
import time

# Save File locations into string
ecg_csv= "bioharness/bin/Debug/netcoreapp3.1/Experiment/Session/ecgLog.csv"
rr_csv= "bioharness/bin/Debug/netcoreapp3.1/Experiment/Session/breathingLog.csv"

def process_ecg():
    ecg_df = pd.read_csv(ecg_csv, skiprows=1, header=None)
    ecg_activity = ecg_df[ecg_df.columns[0]]
    ecg_timestamp = round(ecg_df[ecg_df.columns[1]], 2)# Round time to two dp
    ecg_entries = ecg_activity[500:] # Change number to match entries made every 5 seconds
    
    # Convert ecg_entries to a numerical array
    ecg_entries = pd.to_numeric(ecg_entries, errors='coerce')
    
    signals, info = nk.ecg_process(ecg_entries, sampling_rate=250)
    
    # Get RMSSD of all entries
    # hrv_time = nk.hrv_time(signals["ECG_R_Peaks"], sampling_rate=250)
    hrv_indices = nk.hrv(signals, sampling_rate=250, show=False)
    rmssd = hrv_indices['HRV_RMSSD']
    
    # Creating Dataframes
    ecg_dataframe = pd.DataFrame({'HRV RMSSD': rmssd,
                                  'HRV RMSSD Timestamp': ecg_timestamp})

    return ecg_dataframe
    
def process_rr():
    rr_df = pd.read_csv(rr_csv,skiprows=1, header=None)
    rr_rate = rr_df[rr_df.columns[0]]
    rr_timestamp = round(rr_df[rr_df.columns[1]], 2) # Round time to two dp
    rr_entries = rr_rate[100:] # Change number to match entries made every 5 seconds
    
    rr_entries = pd.to_numeric(rr_entries, errors='coerce')
    
    signals, info = nk.rsp_process(rr_entries, sampling_rate=100)
    
    rav = nk.rsp_rav(signals['RSP_Amplitude'], peaks=signals['RSP_Peaks'])
     
    # Creating Dataframes
    rr_dataframe = pd.DataFrame({'RR Rate': rr_rate, 
                                  'RR Rate Timestamp' : rr_timestamp})

    return rr_dataframe


def main():
    os.makedirs('/output', exist_ok=True)

    while(True):
        # while running, wait 5 seconds before running everything
        
        
        # Reads csv files and collects the ecg activity and timestamp in own location (Run as co-routines)
        
        # Process data and save to dataframes
        ecg_dataframe = process_ecg()
        rr_dataframe = process_rr()
        
        # Save to seperate csv files
        ecg_dataframe.to_csv("/output/ecg_output.csv")
        rr_dataframe.to_csv("/output/rr_output.csv")
        
        time.sleep(5)
        
        # If key is pressed, quit program
        if keyboard.is_pressed('P'):
            ecg_dataframe.to_csv("/output/ecg_output.csv")
            rr_dataframe.to_csv("/output/rr_output.csv")
            exit(0)

if __name__ == '__main__':
    main()