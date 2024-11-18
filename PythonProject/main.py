# Load NeuroKit and other useful packages
import neurokit2 as nk
import pandas as pd
import numpy as np
import os
import time
import logging

# Save File locations into string
ecg_csv= "bioharness/bin/Debug/netcoreapp3.1/Experiment/Session/ecgLog.csv"
rr_csv= "bioharness/bin/Debug/netcoreapp3.1/Experiment/Session/breathingLog.csv"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_ecg():
    try:
        # Opens csv and reads columns within the csv
        ecg_df = pd.read_csv(ecg_csv, skiprows=[0], skipfooter=[-1], header=None)
        
        if ecg_df.empty:
            logging.error("ECG DataFrame is empty.")
            return None

        ecg_activity = ecg_df[ecg_df.columns[0]].tolist()
        ecg_timestamp = round(ecg_df[ecg_df.columns[1]], 2)
        
        ecg_activity = pd.to_numeric(ecg_activity, errors='coerce')
        
        ecg_entries = ecg_activity[-2500:] # Change number to match entries made every 5 seconds


        # Convert ECG activity to numpy array
        ecg_entries = np.array(ecg_activity[-2500:])
        
        # Drop empty elements
        ecg_entries = ecg_entries[~np.isnan(ecg_entries)]
        
        # Default processing pipeline
        signals, info = nk.ecg_process(ecg_entries, sampling_rate=250)
        
        peaks, info = nk.ecg_peaks(ecg_entries, sampling_rate=250)
        
        hrv_time = nk.hrv_time(peaks, sampling_rate=250, show=True)
        
        if 'HRV_RMSSD' in hrv_time:
            rmssd = hrv_time['HRV_RMSSD']
        else:
            logging.warning("HRV RMSSD could not be calculated.")
            return None
        
        logging.info(f"HRV RMSSD: {hrv_time['HRV_RMSSD']}")
        
    except Exception as e:
        logging.error(f"Error in process_ecg: {str(e)}")
        return None
    
    # Creating Dataframes
    ecg_dataframe = pd.DataFrame({'HRV RMSSD': rmssd,
                                  'HRV RMSSD Timestamp': ecg_timestamp})

    return ecg_dataframe
    
def process_rr():
    rr_df = pd.read_csv(rr_csv,skiprows=1, header=None)

    rr_rate = rr_df[rr_df.columns[0]]
    rr_timestamp = round(rr_df[rr_df.columns[1]], 2) # Round time to two dp
    rr_entries = rr_rate[-50:] # Change number to match entries made every 5 seconds
    
    rr_entries = pd.to_numeric(rr_entries, errors='coerce')
    
    # Drop empty element
    rr_entries = rr_entries.dropna(inplace=True)

    
    print(rr_entries)
    
    # signals, info = nk.rsp_process(rr_entries, sampling_rate=100)
    
    # rav = nk.rsp_rav(signals['RSP_Amplitude'], peaks=signals['RSP_Peaks'])
     
    # # Creating Dataframes
    # rr_dataframe = pd.DataFrame({'RR Rate': rr_rate, 
    #                               'RR Rate Timestamp' : rr_timestamp})

    # return rr_dataframe


def main():
    # Create dir if it isn't made already
    os.makedirs('output', exist_ok=True)

    while True:
        # while running, wait 5 seconds before running everything
        time.sleep(5)
        
        try:
            # Process data and save to dataframes
            hrv_result = process_ecg()
            #rr_result = process_rr()
            
            if hrv_result:
                # Save to separate csv files
                hrv_result.to_csv("output/hrv_output.csv")
                #rr_result.to_csv("output/rr_output.csv")
                
                logging.info("Data processed and saved successfully")
            else:
                logging.warning("Failed to process data. Check logs for details.")
        except Exception as e:
            logging.error(f"Main loop error: {str(e)}")
            

if __name__ == '__main__':
    main()