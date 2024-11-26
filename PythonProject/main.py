# Load NeuroKit and other useful packages
import neurokit2 as nk
import pandas as pd
import numpy as np
import time
import logging

# Save File locations into string
ecg_csv = "bioharness/bin/Debug/netcoreapp3.1/Experiment/Session/ecgLog.csv"
rsp_csv = "bioharness/bin/Debug/netcoreapp3.1/Experiment/Session/breathingLog.csv"

collected_df = df = pd.DataFrame(columns=['ECG RMSSD', 'RSP Rate'])

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_data():
    try:
        # Read in csv's and turn them into numpy arrays
        ecg_df = pd.read_csv(ecg_csv, skiprows=1, header=None, engine='python')
        rsp_df = pd.read_csv(rsp_csv, skiprows=1, header=None, engine='python')

        # Drop empty
        ecg_df = ecg_df[pd.to_numeric(ecg_df[0], errors='coerce').notnull()]
        rsp_df = rsp_df[pd.to_numeric(rsp_df[0], errors='coerce').notnull()]

        # Removing empty cells from csv
        ecg_extracted_entries = ecg_df.dropna()
        rsp_extracted_entries = rsp_df.dropna()

        # Delete last 10 entries to avoid incomplete data
        ecg_extracted_entries = ecg_extracted_entries[:-10]
        rsp_extracted_entries = rsp_extracted_entries[:-10]

        # Seperate columns and switch to one-dimensional arrays
        ecg_data = np.array(ecg_extracted_entries.iloc[:, 0], dtype=float)
        rsp_data = np.array(rsp_extracted_entries.iloc[:, 0], dtype=float)

        ecg_timestamp = np.array(ecg_extracted_entries.iloc[:, 1], dtype=float)
        rsp_timestamp = np.array(rsp_extracted_entries.iloc[:, 1], dtype=float)

        logging.info("Columns created.")
        logging.info(f"Entries extracted successfully")
        logging.info("Entries turned into one dimensional arrays.")

    except FileNotFoundError:
        logging.error(f"File not found: {ecg_csv} or {rsp_csv}")
    except Exception as e:
        logging.error(f"Error reading CSV files or extracting data: {str(e)}")

    try:
        # Process signals
        ecg_signals, ecg_info = nk.ecg_process(ecg_data, sampling_rate=1000)
        rsp_signals, rsp_info = nk.rsp_process(rsp_data, sampling_rate=25)

        # get hrv
        ecg_peaks, _ = nk.ecg_peaks(ecg_signals, sampling_rate=1000)
        ecg_hrv = nk.hrv_time(ecg_peaks, sampling_rate=1000)

        # Get the value from HRV_RMSSD, and convert it to a float
        ecg_RMSSD = ecg_hrv['HRV_RMSSD'].values[0].item()
        logging.info(f"RMSSD calculated: {str(ecg_RMSSD)}")

        # get rsp rate
        rsp_rrv = nk.rsp_rrv(rsp_signals, sampling_rate=25)

        # Get the value from RRV_RMSSD, and convert it to a float
        rsp_rate = rsp_rrv['RRV_RMSSD'].values[0].item()
        logging.info(f"RRV RMSSD calculated: {str(rsp_rate)}")

        # Return ecg and rsp data to be turned into csv file
        return ecg_RMSSD, rsp_rate
    except Exception as e:
        logging.error(f"Error processing signals {str(e)}")
        return None, None


def data_to_dataframes(ecg_RMSSD, rsp_rate):
    logging.info("Starting Data Collation")
    try:
        # Collect data and collate in correct format
        temp_data = {'ECG RMSSD': [ecg_RMSSD],
                     'RSP Rate': [rsp_rate]}

        # add to new dataframe
        collected_df.loc[len(collected_df)] = temp_data

        # Convert to CSV
        collected_df.to_csv('output/collected_dataframe.csv')
        logging.info("Data written to CSV")
    except Exception as e:
        logging.error(f"Error writing data to CSV: {str(e)}")


def main():
    while True:
        try:
            time.sleep(5)
            ecg_rmssd, rsp_rate = process_data()
            if ecg_rmssd is not None and rsp_rate is not None:
                data_to_dataframes(ecg_rmssd, rsp_rate)
            else:
                logging.warning("Data processing failed, skipping iteration")
        except Exception as e:
            logging.error(f"Error in main loop: {str(e)}")


if __name__ == '__main__':
    main()
