# Load NeuroKit and other useful packages
import neurokit2 as nk
import pandas as pd
import numpy as np
import os
import time
import logging

# Save File locations into string
ecg_csv= "bioharness/bin/Debug/netcoreapp3.1/Experiment/Session/ecgLog.csv"
rsp_csv= "bioharness/bin/Debug/netcoreapp3.1/Experiment/Session/breathingLog.csv"

collected_df = df = pd.DataFrame(columns=['ECG RMSSD', 'RSP Rate'])

def process_data():
    # Read in csv's and turn them into numpy arrays
    ecg_df = pd.read_csv(ecg_csv, skipheader=1, skipfooter=1, header=None, engine='python')
    rsp_df = pd.read_csv(rsp_csv, skipheader=1, skipfooter=1, header=None, engine='python')
    
    # Get activity columns from rsp and ECG
    ecg_data = ecg_df[ecg_data.columns[0]]
    rsp_data = rsp_df[rsp_data.columns[0]]
    
    ecg_timestamp = ecg_df[ecg_data.columns[1]]
    rsp_timestamp = rsp_df[rsp_data.columns[1]]
    
    ecg_extrated_entries = ecg_data[-5000:]
    rsp_extracted_entries = rsp_data[-2000:]
    
    # Turn into numpy arrays
    ecg_extracted_entries = pd.to_numeric(ecg_extrated_entries)
    rsp_extracted_entries = pd.to_numeric(rsp_extracted_entries)
    
    # Clean signals
    ecg_cleaned_entries = nk.ecg_clean(ecg_extracted_entries, sampling_rate=1000)
    rsp_cleaned_entries = nk.rsp_clean(rsp_extracted_entries, sampling_rate=25)
    
    # Process signals
    ecg_signals = nk.ecg_process(ecg_cleaned_entries, sampling_rate=1000)
    rsp_signals = nk.rsp_process(rsp_cleaned_entries, sampling_rate=25)
    
    # get hrv
    ecg_hrv = nk.hrv(ecg_signals, sampling_rate=1000)
    ecg_RMSSD = ['HRV'] # Extracts RMSSD from hrv
    
    # get rsp rate
    rsp_rate = rsp_signals['rsp_rate']
    
    # Return ecg and rsp data to be turned into csv file
    return ecg_RMSSD, rsp_rate
    
def data_to_dataframes(ecg_RMSSD, rsp_rate):
    # Collect data and collate in correct format
    temp_data = {'ECG RMSSD' : [ecg_RMSSD],
                'RSP Rate' : [rsp_rate]}
    
    # add to new dataframe
    collected_df.append(temp_data)
    
    # Convert to CSV
    collected_df.to_csv('output/collected_dataframe.csv')

def main():
    while(True):
        time.sleep(5)
        ecg_RMSSD, rsp_rate = process_data()
        data_to_dataframes(ecg_RMSSD, rsp_rate)


if __name__ == '__main__':
    main()