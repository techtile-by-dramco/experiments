Experiment just boots up and transmits.

This is to check the different perceived phase differences between 2 USRP tx RF chains.

This test if the observed phase difference is only due to the initial state of the USRP + phase delay in cabling + phase due to DIV.

![image](https://github.com/user-attachments/assets/94d72650-9755-4963-82cb-0c7a6185680e)


Expectation:

| Frequency | Expected number of phase diff | Observed number of phase diff |
| --- | --- |  --- |
| 400 MHz | 16 | 13 |
| 800 MHz | 8 | 8 |
| 4 GHz | 2 | 2 |

![image](https://github.com/user-attachments/assets/2a72660b-e47e-409f-aca3-3ea1ca873937)



![image](https://github.com/user-attachments/assets/29cd251b-e5d6-4ada-80e6-605c5fd79853)

