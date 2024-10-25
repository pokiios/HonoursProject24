# Load NeuroKit and other useful packages
import neurokit2 as nk
import pandas as pd
import numpy as np
import seaborn as sns

# Download data
data = nk.data("bio_eventrelated_100hz")

condition_list = ["Negative", "Neutral", "Neutral", "Negative"]

# Find events
events = nk.events_find(data["Photosensor"], threshold_keep='below', event_conditions=condition_list)

# Plot the location of event with the signals
plot = nk.events_plot(events, data)

# Process the signal
data_clean, info = nk.bio_process(ecg=data["ECG"],
                                  rsp=data["RSP"],
                                  eda=data["EDA"],
                                  keep=data["Photosensor"],
                                  sampling_rate=100)

# Visualize some of the channels
data_clean[["ECG_Rate", "RSP_Rate", "EDA_Phasic", "Photosensor"]].plot(subplots=True)

# Build and plot epochs
epochs = nk.epochs_create(data_clean, events, sampling_rate=100, epochs_start=-1, epochs_end=6)

# Iterate through epoch data
for epoch in epochs.values():
    # Plot scaled signals
    nk.signal_plot(epoch[['ECG_Rate', 'RSP_Rate']],
                   title=epoch['Condition'].values[0],  # Extract condition name
                   standardize=True)

df = {}  # Initialize an empty dict to store the results

# Iterate through epochs index and data
for epoch_index, epoch in epochs.items():
    df[epoch_index] = {}  # Initialize an empty dict inside of it

    # Note: We will use the 100th value (corresponding to the event onset, 0s) as the baseline

    # ECG ====
    ecg_baseline = epoch["ECG_Rate"].values[100]  # Baseline
    ecg_mean = epoch["ECG_Rate"][0:4].mean()  # Mean heart rate in the 0-4 seconds
    # Store ECG in df
    df[epoch_index]["ECG_Rate_Mean"] = ecg_mean - ecg_baseline  # Correct for baseline

    # RSP ====
    rsp_baseline = epoch["RSP_Rate"].values[100]  # Baseline
    rsp_rate = epoch["RSP_Rate"][0:6].mean()  # Longer window for RSP that has a slower dynamic
    # Store RSP in df
    df[epoch_index]["RSP_Rate_Mean"] = rsp_rate - rsp_baseline  # Correct for baseline

df = pd.DataFrame.from_dict(df, orient="index")  # Convert to a dataframe
df["Condition"] = condition_list  # Add the conditions
print(df)

df = nk.bio_analyze(epochs, sampling_rate=100)
print(df)