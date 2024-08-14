
# %%

visa_address = 'TCPIP::192.108.0.251::INSTR'

import time # std module
import pyvisa as visa # http://github.com/hgrecco/pyvisa
import matplotlib.pyplot as plt # http://matplotlib.org/
import numpy as np # http://www.numpy.org/
# from tqdm import tqdm
from scipy.signal import find_peaks

rm = visa.ResourceManager()
scope = rm.open_resource(visa_address)
scope.timeout = 10000 # ms
scope.encoding = 'latin_1'
scope.read_termination = '\n'
scope.write_termination = None
scope.write('*cls') # clear ESR
scope.write('*rst') # reset
r = scope.query('*opc?') # sync

# print(scope.query('SET?'))

print(scope.query('*idn?'))

# Channel 1 50Ohm 2GHz
scope.write("CH1:TERMINATION 50")
scope.write("CH1:BANDWIDTH 2.0000E+9")


print(scope.query(':CH1:TERMINATION?'))
print(scope.query(':CH1:BANdwidth?'))

# open spectrum view
# spectrum view 910MHz and 100kHz BW

scope.write("DISplay:SELect:SPECView1:SOUrce CH1")
scope.write("CH1:SV:STATE ON")
scope.write("CH1:SV:CENTERFrequency 910.0015E+06")
scope.write("SV:SPAN 3.0E+03")
# scope.write("SV:SPAN 6.0E+03")

scope.write("SV:RBWMode MANUAL")
# scope.write("SV:RBW 3.0E+00")
scope.write("SV:RBW 3.0E+00")

scope.write("SV:CH1:UNIts DBM")

# scope.write("SV:RBW 2.0E+06")

scope.write("DATa:SOUrce CH1_SV_NORMal")

print(scope.query("DATa:SOUrce?"))

scope.write("DATa:START 1")
scope.write("DATa:STOP 1901")

print(scope.query("DATa:STARt?"))
print(scope.query("DATa:STOP?"))

time.sleep(2)

print(scope.query("WFMOutpre:SPAN?"))
scope.write("WFMOutpre:BYT_Or LSB")

print(scope.query("DATA:WIDTH?"))
print(scope.query(":WFMOutpre?"))

print(scope.query("WFMOutpre:NR_Pt?"))


time.sleep(2)


r = scope.query('*opc?') # sync


# %%
positions = []
measurements_per_pos = []

pwr_dbm = scope.query_binary_values("CURVe?", datatype='d', container=np.array)

power_linear = 10 ** (pwr_dbm / 10)
tot_pwr_dbm = float(10*np.log10(np.sum(power_linear))) #float to cast to single element
print(tot_pwr_dbm)

# Only peaks
pwr_dbm_filter = pwr_dbm[pwr_dbm > -80]
peaks,_ = find_peaks(pwr_dbm_filter)
power_linear = 10 ** (pwr_dbm_filter[peaks] / 10)
tot_pwr_dbm = float(10*np.log10(np.sum(power_linear))) #float to cast to single element
print(f"NO peaks: {len(peaks)} - Pwr [dBm]: {tot_pwr_dbm}")
print(pwr_dbm_filter[peaks])
