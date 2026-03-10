import nidaqmx
from nidaqmx.constants import AcquisitionType, TerminalConfiguration
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import numpy as np
import csv
from datetime import datetime

# --- Configuration ---
DEVICE_NAME = "cDAQ1Mod1" 
CHANNELS = 8
SAMPLE_RATE = 1000  # Hz
WINDOW_SIZE = 500   # Number of points shown on graph

# Global State
is_paused = False
data_log = []

def toggle_pause(event):
    global is_paused
    is_paused = not is_paused
    pause_btn.label.set_text('Resume' if is_paused else 'Pause')

def save_to_csv(event):
    if not data_log:
        print("No data to save yet.")
        return
    
    filename = f"scan_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([f"Ch {i}" for i in range(CHANNELS)])
        writer.writerows(data_log)
    print(f"Saved {len(data_log)} samples to {filename}")

# Setup Plot
fig, ax = plt.subplots(figsize=(10, 6))
plt.subplots_adjust(bottom=0.2) # Make room for buttons
lines = [ax.plot([], [], label=f'Ch {i}')[0] for i in range(CHANNELS)]
ax.set_ylim(-1, 10)
ax.set_xlim(0, WINDOW_SIZE)
ax.legend(loc='upper right', ncol=4)

# UI Buttons
ax_pause = plt.axes([0.7, 0.05, 0.1, 0.075])
ax_save = plt.axes([0.81, 0.05, 0.1, 0.075])
pause_btn = Button(ax_pause, 'Pause')
save_btn = Button(ax_save, 'Save CSV')
pause_btn.on_clicked(toggle_pause)
save_btn.on_clicked(save_to_csv)

# Buffers
plot_buffer = np.zeros((CHANNELS, WINDOW_SIZE))

# Start DAQ Task
with nidaqmx.Task() as task:
    task.ai_channels.add_ai_voltage_chan(
        f"{DEVICE_NAME}/ai0:{CHANNELS-1}",
        terminal_config=TerminalConfiguration.RSE
    )
    
    # Configure continuous sampling
    task.timing.cfg_samp_clk_timing(
        rate=SAMPLE_RATE,
        sample_mode=AcquisitionType.CONTINUOUS
    )

    print("Recording... Close the window to stop.")
    
    while plt.fignum_exists(fig.number):
        # Read 100 samples at a time
        new_data = task.read(number_of_samples_per_channel=100)
        new_data_array = np.array(new_data)
        
        # Always log data in the background (even if paused)
        for i in range(len(new_data_array[0])):
            data_log.append(new_data_array[:, i].tolist())

        if not is_paused:
            # Shift buffer and add new data
            plot_buffer = np.roll(plot_buffer, -100, axis=1)
            plot_buffer[:, -100:] = new_data_array
            
            for i, line in enumerate(lines):
                line.set_data(range(WINDOW_SIZE), plot_buffer[i])
            
        plt.pause(0.01) # Required for UI updates