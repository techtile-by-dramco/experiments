Experiment just boots up and transmits.

This is to check the different perceived phase differences between 2 USRP tx RF chains.

This test if the observed phase difference is only due to the initial state of the USRP + phase delay in cabling + phase due to DIV.

![image](https://github.com/user-attachments/assets/94d72650-9755-4963-82cb-0c7a6185680e)



with 16-port splitter


uhd_siggen --args "mode_n=integer" --freq 920e6 --clock-source 'external' --sync 'pps' --const -g 80 --offset 0 -m 0.8


python .\sync-server.py 2 2

