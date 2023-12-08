

visa_address = 'TCPIP::192.108.0.251::INSTR'

import time # std module
import pyvisa as visa # http://github.com/hgrecco/pyvisa
import matplotlib.pyplot as plt # http://matplotlib.org/
import numpy as np # http://www.numpy.org/

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
scope.write("SV:CH1:UNIts DBM")

# scope.write("SV:RBW 2.0E+06")

scope.write("DATa:SOUrce CH1_SV_NORMal")

print(scope.query("DATa:SOUrce?"))

scope.write("DATa:STOP 1901")

print(scope.query("DATa:STARt?"))
print(scope.query("DATa:STOP?"))

time.sleep(2)

print(scope.query("WFMOutpre:SPAN?"))

print(scope.query("DATA:WIDTH?"))
print(scope.query(":WFMOutpre?"))

time.sleep(1)

pwr_dbm = scope.query_binary_values("CURVe?", datatype='d', container=np.array)
power_linear = 10 ** (pwr_dbm / 10)
pwr_sum_lin = np.sum(power_linear)
tot_pwr_dbm = 10*np.log10(pwr_sum_lin)
print(tot_pwr_dbm)

# print(len(list))
# print(list)

x = np.linspace(1, len(pwr_dbm), len(pwr_dbm))

fig = plt.figure(figsize=(14, 7))
plt.plot(x, pwr_dbm)
plt.show()

# scope.query_binary_values('fetch:avtime:first?', datatype='f', container=np.array)

# for i in range(10):
#     print(list[i])

# arr = bytes(list, 'utf-8')
#
# print(arr)
# print(len(arr))

# print(scope.query("CURVe?"))

# print(scope.query("CH1:SV?"))

# print(scope.query("DISplay:SELect:SPECView1:SOUrce?"))

exit()

scope.write("SV:MARKER:PEAK:THReshold -80")

print(scope.query("SV:MARKER:PEAK:THReshold?"))


while 1:
    time.sleep(0.5)
    print(scope.query("SV:MARKER:PEAKS:AMPLITUDE?"))
    print(scope.query("SV:MARKER:PEAKS:FREQuency?"))

# print(scope.query("Curve?"))

exit()

scope.write("PEAKSTABLE:ADDNEW 'Table1'")

scope.write("PEAKSTABle:TABle<x>:FRESolution PRECISE")

time.sleep(1)

while 1:
    time.sleep(0.5)
    print(scope.query("SV:MARKER:PEAKS:AMPLITUDE?"))
    print(scope.query("SV:MARKER:PEAKS:FREQuency?"))

# print(scope.query("MEASUrement:MEAS1:CCRESUlts:CURRentacq:MEAN?"))

exit()

scope.write("MEASUrement:ADDMEAS CPOWER")

print(scope.query('MEASUrement?'))
print('***** Measurement with unit and other tags:')
print(scope.query('MEASUrement:MEAS1:VALUE?;YUNIT?;TYPE?;SOUR1?'))
print('***** Measurement with unit and other tags:')
meas = float(scope.query("MEASUrement:MEAS2:resu:curr:mean?"))
print(meas)

############ OUTPUT ##############
# ***** Measurement with unit and other tags:
# 9.91E+37;"";CPOWER;CH1_SV_NORMAL
# ***** Measurement with unit and other tags:
# 9.91e+37
############ OUTPUT ##############



scope.close()
rm.close()
