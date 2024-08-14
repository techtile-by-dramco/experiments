import zmq
import threading
import json
import time

from datetime import datetime,timezone


class ep_data(object):
    def __init__(self, buffer_voltage_mv, resistance, pwr_nw):
        self.buffer_voltage_mv=buffer_voltage_mv
        self.resistance=resistance
        self.pwr_nw=pwr_nw
    
    def json_decoder(obj):
        if obj is not None:
            return ep_data(buffer_voltage_mv=obj["buffer_voltage_mv"], resistance=obj["resistance"],pwr_nw=obj["pwr_nw"])
           
    def __str__(self) -> str:
        return f"{self.buffer_voltage_mv} mV, {self.resistance} Ohm, {self.pwr_nw} nW"
    
    def to_csv(self):
        return [self.buffer_voltage_mv,self.resistance,self.pwr_nw]
    
    def get_csv_header(self):
        return ["buffer_voltage_mv","resistance","pwr_nw"]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ep_data):
            return False
        return self.buffer_voltage_mv==other.buffer_voltage_mv and self.resistance==other.resistance and self.pwr_nw==other.pwr_nw



class RFEP():
    def __init__(self, ip:str, port:str) -> None:
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect(f"tcp://{ip}:{port}")
        self.socket.setsockopt_string(zmq.SUBSCRIBE, "")

        #   Set timeout
        self.socket.setsockopt(zmq.RCVTIMEO, 1000)  # Timeout after 1 second (1000 milliseconds)

        #   Define a shared 'stop' flag to control the thread
        self.stop_flag = threading.Event()

        #   Create and link function to this new thread
        self.ep_thread = threading.Thread(target=self.rfep_thread)

        #   Start thread
        self.ep_thread.start()

        self.last_ep_data = None
        self.last_sent = None

    def stop(self):
        #   Set the stop flag to signal the thread to exit
        self.stop_flag.set()

        #   Wait for the thread to complete
        self.ep_thread.join()
        
        #   Close ZMQ socket
        self.socket.close()
        self.context.term()

        #   Confirm with sending a message to the user
        print("Energy profiler thread successfully terminated.")

    def get_data(self) -> ep_data:
        #return last position if its fresh enough or if its changed
        if self.last_ep_data is None:
            return None
        
        if self.last_sent is None:
            self.last_sent = self.last_ep_data
            return self.last_ep_data
        
        if self.last_sent is not self.last_ep_data:
            self.last_sent = self.last_ep_data
            return self.last_ep_data
        
        return None


    def rfep_thread(self):
        while not self.stop_flag.is_set():
            try:
                # Receive the reply from the server for the first request
                message = self.socket.recv_string()
                self.last_ep_data = json.loads(message, object_hook=ep_data.json_decoder)
                print(self.last_ep_data)
            except zmq.error.Again as e:
                # Handle timeout error
                print("EP Thread: Socket receive timed out:", e)




