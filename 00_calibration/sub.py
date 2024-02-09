import zmq
import numpy as np
from datetime import datetime
import sys

TOPIC_CH0 = b"CH0"
TOPIC_CH1 = b"CH1"

FILE_CH0_prefix = "received_data_CH0"  # Binary file for topic CH0
FILE_CH1_prefix = "received_data_CH1"  # Binary file for topic CH1

def receive_numpy_array(ip):
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(f"tcp://{ip}:{50001}")  # Connect to the publisher's address
    
    # Subscribe to topics
    socket.subscribe(TOPIC_CH0)
    socket.subscribe(TOPIC_CH1)

    # Get current UTC timestamp
    timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")

    # Construct file names with UTC timestamp
    file0 = f"{FILE_CH0_prefix}_{timestamp}.dat"
    file1 = f"{FILE_CH1_prefix}_{timestamp}.dat"
    
    with open(file0, 'ab') as file_ch0, open(file1, 'ab') as file_ch1:
        try:
            while True:
                 # Receive data with topic
                [topic, data_bytes] = socket.recv_multipart()

                # Determine the file to write based on the topic
                if topic == TOPIC_CH0:
                    file = file_ch0
                elif topic == TOPIC_CH1:
                    file = file_ch1
                else:
                    # Ignore other topics
                    continue

                
                # Determine the number of elements and element size
                num_elements = len(data_bytes) // np.dtype(np.float32).itemsize
                # Write data to file
                file.write(data_bytes)
                file.flush()  # Flush the changes to disk
                
                print(f"Received and saved data ({topic}): {num_elements} samples")
                
                # # Decode bytes to NumPy array
                # received_array = np.frombuffer(data_bytes, dtype=np.float32)
                
                
        except KeyboardInterrupt:
            pass
        finally:
            socket.close()
            context.term()

if __name__ == "__main__":
    ip = sys.argv[1]
    receive_numpy_array(ip)