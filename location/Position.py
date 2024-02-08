import zmq
import threading
import json

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

        self.pos_thread = threading.Thread(target=self.position_thread)

        self.pos_thread.start()

        self.last_pos = None

        self.ttl = ttl

    def stop(self):
        self.pos_thread.stop()


    def get_pos(self) -> Position:
        #return last position if its fresh enough
        now = datetime.now(timezone.utc)
        # TODO implement the freshness with the ttl param
        return self.last_pos


        


    def position_thread(self):
        while True:
            # Receive the reply from the server for the first request
            message = self.socket.recv_string()
            self.last_pos = json.loads(message, object_hook=Position.json_decoder)
            # print(self.last_pos)




