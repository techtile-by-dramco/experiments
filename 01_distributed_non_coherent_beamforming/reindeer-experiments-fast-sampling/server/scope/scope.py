import time # std module
import pyvisa as visa # http://github.com/hgrecco/pyvisa
import numpy as np # http://www.numpy.org/
from scipy.signal import find_peaks
import threading
import csv
from datetime import datetime,timezone
import matplotlib.pyplot as plt
import os

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

        self.init_done = False

        self.cable_loss = cable_loss
        self.csv_file_path = csv_file_path
        self.csv_header = csv_header
    
        #   Define a shared 'stop' flag to control the thread
        self.stop_flag = threading.Event()

        #   Create and link function to this new thread
        self.sc_thread = threading.Thread(target=self.scope_thread)

        #   Start thread
        self.sc_thread.start()


    def stop(self):
        #   Set the stop flag to signal the thread to exit
        self.stop_flag.set()

        #   Wait for the thread to complete
        self.sc_thread.join()
        
        #   Confirm with sending a message to the user
        print("Scope thread successfully terminated.")
    
    def write(self, s:str):
        self.scope.write(s)

    def query(self, s:str):
        return self.scope.query(s)

    def setup(self, bandwidth, center, span, rbw, no_peaks):

        self.span = span
        self.rbw = rbw
        self.no_peaks = no_peaks

        rm = visa.ResourceManager()
        self.scope = rm.open_resource(self.visa_address)
        self.scope.timeout = 10000 # ms
        self.scope.encoding = 'latin_1'
        self.scope.read_termination = '\n'
        self.scope.write_termination = None
        self.scope.write('*cls') # clear ESR
        self.scope.write('*rst') # reset
        r = self.scope.query('*opc?') # sync

        self.scope.query('*idn?')

        # Channel 1 50Ohm 2GHz
        self.scope.write("CH1:TERMINATION 50")
        self.scope.write(f"CH1:BANDWIDTH {bandwidth}")

        self.scope.query(':CH1:TERMINATION?')
        self.scope.query(':CH1:BANdwidth?')

        # Open spectrum view
        # spectrum view 910MHz and 100kHz BW
        self.scope.write("DISplay:SELect:SPECView1:SOUrce CH1")
        self.scope.write("CH1:SV:STATE ON")
        self.scope.write(f"CH1:SV:CENTERFrequency {center}")
        self.scope.write(f"SV:SPAN {self.span}")

        self.scope.write("SV:RBWMode MANUAL")
        self.scope.write(f"SV:RBW {self.rbw}")

        self.scope.write("SV:CH1:UNIts DBM")

        self.scope.write("DATa:SOUrce CH1_SV_NORMal")

        self.scope.query("DATa:SOUrce?")

        data_stop = round(self.span/self.rbw*2)

        self.scope.write("DATa:START 1")
        self.scope.write(f"DATa:STOP {data_stop}")

        self.scope.query("DATa:STARt?")
        self.scope.query("DATa:STOP?")

        time.sleep(2)

        print(self.scope.query("WFMOutpre:SPAN?"))
        self.scope.write("WFMOutpre:BYT_Or LSB")

        self.scope.query("DATA:WIDTH?")
        self.scope.query(":WFMOutpre?")

        print(self.scope.query("WFMOutpre:NR_Pt?"))

        self.init_done = True

    def get_data(self) -> float:
        return self.scope.query_binary_values("CURVe?", datatype='d', container=np.array)


    def calc_full_channel_power(self, data) -> float:
        #pwr_lin = 10 ** (data / 10)
        #tot_pwr_dbm = float(10*np.log10(np.sum(pwr_lin))) #float to cast to single element
        #return tot_pwr_dbm + self.cable_loss

        # Convert dBm to Watts
        power_samples_W = 10**(data / 10) * 1e-3  # Convert dBm to Watts

        # Integrate power samples over the frequency band (each sample corresponds to the RBW)
        total_power_W = np.sum(power_samples_W)

        # Convert total power back to dBm
        total_power_dBm = 10 * np.log10(total_power_W / 1e-3)

        return total_power_dBm

        # print(f"Total channel power: {total_power_dBm:.2f} dBm")
 

    def calc_channel_power_peaks(self, data, search_for_no_peaks) -> float:

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
        return tot_pwr_dbm, peaks        


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


    def scope_thread(self):

        print("Scope thread start")

        while not self.init_done:
            if self.stop_flag.is_set():
                break
        
        print("Scope loop start")

        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.csv_file_path), exist_ok=True)

        with open(self.csv_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)

            #   Write CSV header
            writer.writerow(self.csv_header)

            while not self.stop_flag.is_set():

                #print("scope loop")
                
                #time.sleep(0.1)

                #print(self.scope.query('*opc?'))
                
                # Get data
                pwr_data_dbm = self.get_data()
                #data = [round(time.time_ns()/1e6), self.get_power_dBm(pwr_data_dbm)]
                #print(f"calc_full_channel_power: {self.calc_full_channel_power(pwr_data_dbm)}")
                #print(f"calc_channel_power_peaks: {self.calc_channel_power_peaks(pwr_data_dbm, 84)[0]}")

                channel_power = self.calc_channel_power_peaks(pwr_data_dbm, self.no_peaks)[0]

                data = [round(time.time_ns()/1e6), channel_power]

                #plt.plot(np.linspace(1, len(pwr_data_dbm), len(pwr_data_dbm)), pwr_data_dbm)
                #plt.show()



                # Write data to CSV file
                writer.writerow(data)
