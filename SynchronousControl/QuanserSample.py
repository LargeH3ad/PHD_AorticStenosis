import time
import numpy as np
from quanser.hardware import HIL, HILError

# Device configuration
board_type = "qpid_e"   # QPIDe board type
board_identifier = "0"  # Usually 0 for first device

# Analog input channels to read
ai_channels = np.array([0, 1, 2, 3], dtype=np.uint32)

# Buffer for values
ai_buffer = np.zeros(len(ai_channels), dtype=np.float64)

try:
    print("Attempting to connect to QPIDe...")

    # Create board object
    card = HIL()

    # Open device
    card.open(board_type, board_identifier)

    print("Device connected successfully.")

    # Start streaming loop
    print("Streaming analog input values... Press Ctrl+C to stop.")

    while True:
        # Read analog channels
        card.read_analog(ai_channels, len(ai_channels), ai_buffer)

        # Print values
        print("Analog values:", ai_buffer)

        time.sleep(0.1)

except HILError as e:
    print("Quanser HIL Error:", e.get_error_message())

except KeyboardInterrupt:
    print("\nStopping stream.")

finally:
    try:
        card.close()
        print("Device closed.")
    except:
        pass