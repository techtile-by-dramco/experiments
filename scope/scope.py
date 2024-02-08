import time # std module
import pyvisa as visa # http://github.com/hgrecco/pyvisa
import numpy as np # http://www.numpy.org/

from enum import Enum
class ScopeMode(Enum):
    # TODO
    POWER = 1

class Scope:
    """_summary_

    Usage:
        scope = Scope("192.108.0.251")
        power_dBm = scope.get_power_dBm()
    """
    def __init__(self, ip:str, mode:ScopeMode=ScopeMode.POWER) -> None:
        self.visa_address = f'TCPIP::{ip}::INSTR'
    
        self.setup()
    
    def write(self, s:str):
        self.scope.write(s)

    def query(self, s:str):
        self.scope.query(s)

    def setup(self):
        #TODO make this configurable
        rm = visa.ResourceManager()
        self.scope = rm.open_resource(self.visa_address)
        self.scope.timeout = 10000 # ms
        self.scope.encoding = 'latin_1'
        self.scope.read_termination = '\n'
        self.scope.write_termination = None
        self.write('*cls') # clear ESR
        self.write('*rst') # reset
        _ = self.query('*opc?') # sync

        # Channel 1 50Ohm 2GHz
        self.write("CH1:TERMINATION 50")
        self.write("CH1:BANDWIDTH 2.0000E+9")
        
        # open spectrum view
        # spectrum view 910MHz and 100kHz BW
        self.write("DISplay:SELect:SPECView1:SOUrce CH1")
        self.write("CH1:SV:STATE ON")
        self.write("CH1:SV:CENTERFrequency 910.0015E+06")
        self.write("SV:SPAN 3.0E+03")

        self.write("SV:RBWMode MANUAL")
        self.write("SV:RBW 3.0E+00")

        self.write("SV:CH1:UNIts DBM")

        self.write("DATa:SOUrce CH1_SV_NORMal")

        self.write("DATa:START 1")
        self.write("DATa:STOP 1901")

        self.write("WFMOutpre:BYT_Or LSB")

        _ = self.query('*opc?') # sync


    def get_power_dBm(self) -> float:
        pwr_dbm = self.scope.query_binary_values("CURVe?", datatype='d', container=np.array)
        pwr_lin = 10 ** (pwr_dbm / 10)
        tot_pwr_dbm = float(10*np.log10(np.sum(pwr_lin))) #float to cast to single element
        return tot_pwr_dbm

