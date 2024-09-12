# Repeated simple setup 003

Test only LB mode and collect phase. To see if presence of weird phase is due to the PLL being active during LB or it is due to a reflection.

### Settings T01 and T04
```
~/experiments/00_calibration/004_repeated_setup $ ./usrp-cal.sh
```


## Reference T02
`uhd_siggen --args "mode_n=integer" --freq 800e6 --clock-source 'external' --sync 'pps' --const -g 68 --offset 0 -m 0.
8 -c 0``

