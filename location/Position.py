import zmq
import threading

from datetime import datetime,timezone




class AcousticPositioner():
    def __init__(self, ip:str, ttl:float=0.0) -> None:
        context = zmq.Context()
        self.socket = context.socket(zmq.SUB)
        self.socket.connect(f"tcp://{ip}:5555")
        self.socket.setsockopt_string(zmq.SUBSCRIBE, "")

        self.pos_thread = threading.Thread(target=self.position_thread)

        self.pos_thread.start()

        self.last_pos = None
        self.last_pos_time = None

        self.ttl = ttl


    def get_pos(self):
        #return last position if its fresh enough
        now = datetime.now(timezone.utc)
        # TODO implement the freshness with the ttl param
        return self.last_pos

        


    def position_thread(self):
        while True:
            # Receive the reply from the server for the first request
            message = self.socket.recv_string()
            #TODO parse value
            print(f"Received reply from server: {message}")




