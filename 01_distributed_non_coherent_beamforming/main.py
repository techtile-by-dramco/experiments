from scope.scope import Scope
from location.Position import AcousticPositioner
import time 



scope = Scope("192.108.0.251")


positioner = AcousticPositioner("192.108.0.15")

while True:
    pos = positioner.get_pos()
    power_dBm = scope.get_power_dBm()

    time.sleep(10)
    