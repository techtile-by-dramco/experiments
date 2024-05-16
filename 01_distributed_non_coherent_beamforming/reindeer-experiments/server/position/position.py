import zmq
import threading
import json
import time

from datetime import datetime,timezone


class position(object):
    def __init__(self, t, x, y, z, rm):#, x_tx, y_tx, z_tx, rm_tx, x_rx, y_rx, z_rx, rm_rx):
        self.t=t
        self.x=x
        self.y=y
        self.z=z
        self.rm=rm
        # self.x_tx=x_tx
        # self.y_tx=y_tx
        # self.z_tx=z_tx
        # self.rm_tx=rm_tx
        # self.x_rx=x_rx
        # self.y_rx=y_rx
        # self.z_rx=z_rx
        # self.rm_rx=rm_rx
    
    def json_decoder(obj):
        if obj is not None:
            return position(t=obj["t"], x=obj["x"],y=obj["y"],z=obj["z"],rm=obj['rotation_matrix'])#,
                            # x_tx=obj["x_tx"],y_tx=obj["y_tx"],z_tx=obj["z_tx"],rm_tx=obj['rotation_matrix_tx'],
                            # x_rx=obj["x_rx"],y_rx=obj["y_rx"],z_rx=obj["z_rx"],rm_rx=obj['rotation_matrix_rx'])
    
    def __str__(self) -> str:
        return f"@({self.x},{self.y},{self.z}) utc={self.t} rm={self.rm}"
    
    def to_csv(self):
        return [self.x,self.y,self.z,self.t,self.rm]#,
                # self.x_tx,self.y_tx,self.z_tx,self.rm_tx,
                # self.x_rx,self.y_rx,self.z_rx,self.rm_rx]
    
    def get_csv_header(self):
        return ["x","y","z","utc","rm"]#,"x_tx","y_tx","z_tx","rm_tx","x_rx","y_rx","z_rx","rm_rx"]
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, position):
            return False
        return self.x==other.x and self.y==other.y and self.z==other.z


class AcousticPositioner():
    def __init__(self, ip:str, port:str) -> None:
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect(f"tcp://{ip}:{port}")
        self.socket.setsockopt_string(zmq.SUBSCRIBE, "")

        #   Set timeout
        self.socket.setsockopt(zmq.RCVTIMEO, 2000)  # Timeout after 2 second (2000 milliseconds)

        #   Define a shared 'stop' flag to control the thread
        self.stop_flag = threading.Event()

        #   Create and link function to this new thread
        self.pos_thread = threading.Thread(target=self.position_thread)

        #   Start thread
        self.pos_thread.start()

        self.last_pos = None
        self.last_sent = None

    def stop(self):
        #   Set the stop flag to signal the thread to exit
        self.stop_flag.set()

        #   Wait for the thread to complete
        self.pos_thread.join()

        #   Close ZMQ socket
        self.socket.close()
        self.context.term()

        #   Confirm with sending a message to the user
        print("Positioning thread successfully terminated.")

    def get_pos(self) -> position:
        #return last position if its fresh enough or if its changed
        if self.last_pos is None:
            return None
        
        if self.last_sent is None:
            self.last_sent = self.last_pos
            return self.last_pos
        
        if self.last_sent is not self.last_pos:
            self.last_sent = self.last_pos
            return self.last_pos
        
        return None


    def position_thread(self):
        while not self.stop_flag.is_set():
            try:
                # Receive the reply from the server for the first request
                message = self.socket.recv_string()
                self.last_pos = json.loads(message, object_hook=position.json_decoder)
            except zmq.error.Again as e:
                # Handle timeout error
                print("Position Thread: Socket receive timed out:", e)



