import zmq
import threading
import json
import time

from datetime import datetime,timezone


class Position(object):
    def __init__(self, t, x, y, z):
        self.t=t
        self.x=x
        self.y=y
        self.z=z
    
    def json_decoder(obj):
        if obj is not None:
            return Position(t=obj["t"], x=obj["x"],y=obj["y"],z=obj["z"])
    
    def __str__(self) -> str:
        return f"@({self.x},{self.y},{self.z}) utc={self.t}"
    
    def to_csv(self):
        return [self.x,self.y,self.z,self.t]
    
    def get_csv_header(self):
        return ["x","y","z","utc"]
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Position):
            return False
        return self.x==other.x and self.y==other.y and self.z==other.z



class AcousticPositioner():
    def __init__(self, ip:str, ttl:float=0.0) -> None:
        context = zmq.Context()
        self.socket = context.socket(zmq.SUB)
        self.socket.connect(f"tcp://{ip}:5555")
        self.socket.setsockopt_string(zmq.SUBSCRIBE, "")

        # self.event = threading.Event()

        self.pos_thread = threading.Thread(target=self.position_thread)

        self.pos_thread.start()

        self.last_pos = None
        self.last_sent = None

        self.ttl = ttl # time to live before position gets outdated (in seconds)
        self.prev_post_time = None

    def stop(self):
        # if self.event.is_set():
        #     self.event.clear()
        self.pos_thread.join()

    def get_pos(self) -> Position:
        #return last position if its fresh enough or if its changed
        if self.last_pos is None:
            return None
        
        if self.last_sent is None:
            self.last_sent = self.last_pos
            return self.last_pos
        
        if self.last_sent is not self.last_pos:
            self.last_sent = self.last_pos
            return self.last_pos

        # if self.prev_post_time is None:
        #     self.last_sent = self.last_pos
        #     print("new pos")
        #     return self.last_pos
        
        # now = time.time()
        # if now > self.prev_post_time + self.ttl:
        #     self.last_sent = self.last_pos
        #     print("timeout")
        #     return self.last_pos
        # elif self.last_pos != self.last_sent:
        #     print("not the same")
        #     self.last_sent = self.last_pos
        #     return self.last_pos
        
        return None


        


    def position_thread(self):
        while True:
            # Receive the reply from the server for the first request
            message = self.socket.recv_string()
            self.last_pos = json.loads(message, object_hook=Position.json_decoder)
            # print(self.last_pos)




