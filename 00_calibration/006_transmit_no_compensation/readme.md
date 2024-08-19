Experiment just boots up and transmits.

This is to check the different perceived phase differences between 2 USRP tx RF chains.

This test if the observed phase difference is only due to the initial state of the USRP + phase delay in cabling + phase due to DIV.

![image](https://github.com/user-attachments/assets/94d72650-9755-4963-82cb-0c7a6185680e)


Expectation:

| Frequency | Expected number of phase diff | Observed number of phase diff |
| --- | --- |
| 400 MHz | 16 | 13 |
| 800 MHz | 8 | 8 |
| 4 GHz | 2 | 2 |

![image](https://github.com/user-attachments/assets/2c5ce4c0-897c-435c-8ffe-c00f30d3d123)

