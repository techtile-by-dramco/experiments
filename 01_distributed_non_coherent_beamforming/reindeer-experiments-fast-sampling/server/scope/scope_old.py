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
    def __init__(self, ip:str, cable_loss, csv_file_path:str, csv_header, mode:ScopeMode=ScopeMode.POWER) -> None:
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

        ##TODO make this configurable
        #rm = visa.ResourceManager()
        #print(rm)
        #print(rm.list_resources())
        #self.scope = rm.open_resource(self.visa_address)
        #self.scope.timeout = 10000 # ms
        #self.scope.encoding = 'latin_1'
        #self.scope.read_termination = '\n'
        #self.scope.write_termination = None
        #self.write('*cls') # clear ESR
        #self.write('*rst') # reset
        #_ = self.query('*opc?') # sync
#
        ## Channel 1 50Ohm 2GHz
        #self.write(f"CH1:TERMINATION 50")
        #self.write(f"CH1:BANDWIDTH {bandwidth}")
        #
        ## open spectrum view
        ## spectrum view 910MHz and 100kHz BW
        #self.write(f"DISplay:SELect:SPECView1:SOUrce CH1")
        #self.write(f"CH1:SV:STATE ON")
        #self.write(f"CH1:SV:CENTERFrequency {center}")
        #self.write(f"SV:SPAN {span}")
#
        #self.write(f"SV:RBWMode MANUAL")
        #self.write(f"SV:RBW {self.rbw}")
#
        #self.write(f"SV:CH1:UNIts DBM")
#
        #self.write(f"DATa:SOUrce CH1_SV_NORMal")
#
        #data_stop = round(self.span/self.rbw*2)
#
        #self.write(f"DATa:START 1")
        #data_stop = 10
        #self.write(f"DATa:STOP {data_stop}")#1901
#
        #self.write(f"WFMOutpre:BYT_Or LSB")
#
        #_ = self.query('*opc?') # sync
        rm = visa.ResourceManager()
        self.scope = rm.open_resource(self.visa_address)
        self.scope.timeout = 10000 # ms
        self.scope.encoding = 'latin_1'
        self.scope.read_termination = '\n'
        self.scope.write_termination = None
        self.scope.write('*cls') # clear ESR
        self.scope.write('*rst') # reset
        r = self.scope.query('*opc?') # sync

        # print(scope.query('SET?'))

        print(self.scope.query('*idn?'))

        # Channel 1 50Ohm 2GHz
        self.scope.write("CH1:TERMINATION 50")
        self.scope.write(f"CH1:BANDWIDTH {bandwidth}")


        print(self.scope.query(':CH1:TERMINATION?'))
        print(self.scope.query(':CH1:BANdwidth?'))

        # open spectrum view
        # spectrum view 910MHz and 100kHz BW

        self.scope.write("DISplay:SELect:SPECView1:SOUrce CH1")
        self.scope.write("CH1:SV:STATE ON")
        self.scope.write(f"CH1:SV:CENTERFrequency {center}")
        self.scope.write(f"SV:SPAN {self.span}")
        # scope.write("SV:SPAN 6.0E+03")

        self.scope.write("SV:RBWMode MANUAL")
        # scope.write("SV:RBW 3.0E+00")
        self.scope.write(f"SV:RBW {self.rbw}")

        self.scope.write("SV:CH1:UNIts DBM")

        # scope.write("SV:RBW 2.0E+06")

        self.scope.write("DATa:SOUrce CH1_SV_NORMal")

        print(self.scope.query("DATa:SOUrce?"))

        data_stop = round(self.span/self.rbw*2)

        self.scope.write("DATa:START 1")
        self.scope.write(f"DATa:STOP {data_stop}")

        print(self.scope.query("DATa:STARt?"))
        print(self.scope.query("DATa:STOP?"))

        time.sleep(2)

        print(self.scope.query("WFMOutpre:SPAN?"))
        self.scope.write("WFMOutpre:BYT_Or LSB")

        print(self.scope.query("DATA:WIDTH?"))
        print(self.scope.query(":WFMOutpre?"))

        print(self.scope.query("WFMOutpre:NR_Pt?"))


    def get_power_dBm(self, cable_loss) -> float:
        self.query('*opc?')
        pwr_dbm = self.scope.query_binary_values("CURVe?", datatype='d', container=np.array)
        pwr_lin = 10 ** (pwr_dbm / 10)
        tot_pwr_dbm = float(10*np.log10(np.sum(pwr_lin))) #float to cast to single element
        return tot_pwr_dbm + cable_loss


    def get_power_dBm_peaks(self, cable_loss, search_for_no_peaks) -> float:

        self.scope.query('*opc?')

        #   Check span adjustments externally
        self.check_span()

        pwr_dbm = None

        #   Get spectrum form scope
        #pwr_dbm = self.scope.query_binary_values("CURVe?", datatype='d', container=np.array)
        self.write("CURVe?")
        try:
            pwr_dbm = self.scope.read_binary_values(datatype='d', container=np.array)
        except visa.errors.VisaIOError as e:
            print(e)
        
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