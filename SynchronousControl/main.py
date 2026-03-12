# Program designed to control all data collection and control modules 
# simultaneously, ensuring synchronized data collection and control 
# actions.

# send and receive serial communication for stepper motor control
# live record OCR text from ultrasound machine
# live stream and send data through a quanser

import subprocess
import threading
import queue
import sys
import time
import os

def reader_thread(process: subprocess.Popen, output_queue: queue.Queue, label: str):
    """Reads stdout from a subprocess and puts lines into the shared output queue (live)."""
    try:
        for line in iter(process.stdout.readline, ''):
            if line:
                output_queue.put(f"[{label}] {line.strip()}")
    except Exception:
        pass  # Process may have ended


def writer_thread(process: subprocess.Popen, input_queue: queue.Queue):
    """Consumes commands from a queue and writes them to the subprocess stdin."""
    while True:
        try:
            data = input_queue.get(timeout=0.1)
            if data is None:  # Shutdown signal
                break
            process.stdin.write(data + '\n')
            process.stdin.flush()
        except queue.Empty:
            continue
        except Exception:
            break


def input_handler(input_queues: dict):
    """Separate thread for non-blocking user input (type commands while everything else runs live)."""
    print("\n=== Centralized Controller Ready ===")
    print("Commands: '2: your message' → Script2 (Serial)")
    print("          '3: your message' → Script3 (OCR)")
    print("          '4: your message' → Script4 (Quanser)")
    print("          'quit'            → Shutdown everything\n")
    
    while True:
        try:
            cmd = input().strip()
            if not cmd:
                continue
            if cmd.lower() == 'quit':
                for q in input_queues.values():
                    q.put(None)
                break
                
            if ':' in cmd:
                prefix, data = [x.strip() for x in cmd.split(':', 1)]
                try:
                    target = int(prefix)
                    if target in input_queues:
                        input_queues[target].put(data)
                    else:
                        print("Invalid script number (use 2, 3 or 4)")
                except ValueError:
                    print("Use format: 2: message   (or 3:, 4:)")
            else:
                print("Use format: 2: message   (or 3:, 4:)")
        except EOFError:
            break
        except Exception as e:
            print(f"Input error: {e}")


if __name__ == "__main__":
    # Shared queues
    output_queue = queue.Queue()
    
    input_q2 = queue.Queue()  # Serial script
    input_q3 = queue.Queue()  # OCR script
    input_q4 = queue.Queue()  # Quanser script
    
    # Launch the three scripts in parallel as independent processes
    try:
        p2 = subprocess.Popen(
            [sys.executable, "PressureGUI.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,               # Line-buffered for live output
            universal_newlines=True
        )
        p3 = subprocess.Popen(
            [sys.executable, "LiveDetect.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        p4 = subprocess.Popen(
            [sys.executable, "QuanserSample.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
    except FileNotFoundError as e:
        print(f"ERROR: Could not find one of the scripts: {e}")
        print("Make sure script2.py, script3.py and script4.py are in the same folder.")
        sys.exit(1)
    except Exception as e:
        print(f"Failed to launch scripts: {e}")
        sys.exit(1)

    # Start reader threads (live output from all scripts)
    threading.Thread(target=reader_thread, args=(p2, output_queue, "Script2 (Serial)"), daemon=True).start()
    threading.Thread(target=reader_thread, args=(p3, output_queue, "Script3 (OCR)"), daemon=True).start()
    threading.Thread(target=reader_thread, args=(p4, output_queue, "Script4 (Quanser)"), daemon=True).start()

    # Start writer threads (send commands to each script)
    threading.Thread(target=writer_thread, args=(p2, input_q2), daemon=True).start()
    threading.Thread(target=writer_thread, args=(p3, input_q3), daemon=True).start()
    threading.Thread(target=writer_thread, args=(p4, input_q4), daemon=True).start()

    # Start input handler (you can type while everything runs live)
    input_queues = {2: input_q2, 3: input_q3, 4: input_q4}
    threading.Thread(target=input_handler, args=(input_queues,), daemon=True).start()

    # Main loop: live display + OCR recording
    ocr_log_path = "ocr_live_record.txt"
    print(f"OCR text will be automatically recorded to: {os.path.abspath(ocr_log_path)}\n")

    try:
        while True:
            # Drain output queue (live printing from all scripts)
            try:
                while True:
                    msg = output_queue.get_nowait()
                    print(msg)
                    
                    # === Live OCR recording ===
                    if msg.startswith("[Script3 (OCR)]"):
                        ocr_text = msg.split("]", 1)[1].strip()
                        with open(ocr_log_path, "a", encoding="utf-8") as f:
                            f.write(ocr_text + "\n")
            except queue.Empty:
                pass
            
            time.sleep(0.01)  # Keep CPU usage low while staying responsive

    except KeyboardInterrupt:
        print("\n\nKeyboard interrupt received - shutting down...")
    finally:
        # Graceful shutdown
        for q in [input_q2, input_q3, input_q4]:
            q.put(None)
        
        for p, name in [(p2, "Script2"), (p3, "Script3"), (p4, "Script4")]:
            if p.poll() is None:  # Still running
                print(f"Terminating {name}...")
                p.terminate()
                try:
                    p.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    p.kill()
        
        print("All scripts stopped. Goodbye!")