import time # std module
import pyvisa as visa # http://github.com/hgrecco/pyvisa
import numpy as np # http://www.numpy.org/
from scipy.signal import find_peaks

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

        self.span = None
    
        #self.setup()
    
    def write(self, s:str):
        self.scope.write(s)

    def query(self, s:str):
        return self.scope.query(s)

    def setup(self, bandwidth, center, span, rbw):

        self.span = span
        self.rbw = rbw

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
        self.write(f"CH1:TERMINATION 50")
        self.write(f"CH1:BANDWIDTH {bandwidth}")
        
        # open spectrum view
        # spectrum view 910MHz and 100kHz BW
        self.write(f"DISplay:SELect:SPECView1:SOUrce CH1")
        self.write(f"CH1:SV:STATE ON")
        self.write(f"CH1:SV:CENTERFrequency {center}")
        self.write(f"SV:SPAN {span}")

        self.write(f"SV:RBWMode MANUAL")
        self.write(f"SV:RBW {self.rbw}")

        self.write(f"SV:CH1:UNIts DBM")

        self.write(f"DATa:SOUrce CH1_SV_NORMal")

        data_stop = round(self.span/self.rbw*2)

        self.write(f"DATa:START 1")
        self.write(f"DATa:STOP {data_stop}")#1901

        self.write(f"WFMOutpre:BYT_Or LSB")

        _ = self.query('*opc?') # sync


    def get_power_dBm(self, cable_loss) -> float:
        pwr_dbm = self.scope.query_binary_values("CURVe?", datatype='d', container=np.array)
        pwr_lin = 10 ** (pwr_dbm / 10)
        tot_pwr_dbm = float(10*np.log10(np.sum(pwr_lin))) #float to cast to single element
        return tot_pwr_dbm + cable_loss


    def get_power_dBm_peaks(self, cable_loss, search_for_no_peaks) -> float:

        #   Check span adjustments externally
        self.check_span()

        #   Get spectrum form scope
        pwr_dbm = self.scope.query_binary_values("CURVe?", datatype='d', container=np.array)
        
        #   Calculate all peaks in spectrum
        peaks,_ = find_peaks(pwr_dbm)
        #print(pwr_dbm[peaks])

        #   Sort peaks in descending order
        peaks_sorted = sorted(pwr_dbm[peaks], reverse=True)
        # print(peaks_sorted[:search_for_no_peaks])

        #   Combine peaks to one overall power value
        power_linear = 10 ** (np.asarray(peaks_sorted[:search_for_no_peaks]) / 10)
        #print(power_linear)
        tot_pwr_dbm = float(10*np.log10(np.sum(power_linear))) #float to cast to single element
        return tot_pwr_dbm + cable_loss, peaks        


    def check_span(self):
        new_span = float(self.query(f"SV:SPAN?"))
        if new_span != self.span:
            
            #   Warning
            print("Span changed externally!")

            #   Update span value
            self.span = new_span

            data_stop = round(self.span/self.rbw*2)

            self.write(f"DATa:START 1")
            self.write(f"DATa:STOP {data_stop}")#1901