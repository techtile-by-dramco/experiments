# This is a simple setup to test if we can get the USRPs phase synchronized using an external USRP as reference

![image](https://github.com/techtile-by-dramco/experiments/assets/8626571/1db06b0d-3859-4b75-bd3f-593b0993bf9e)



## Setup description


All USRPs (3) are being fed by the same PPS and 10MHz. This is done by using 2-way splitters.
**No** PLL board was attached, but the FPGA loopback was used. Hence, LO leakage was exploited.

### Reference USRP (Tile 2)

1 USRP is used as a reference and is transmitting:
```sh
uhd_siggen --args "mode_n=integer, fpga=usrp_b210_fpga_loopback.bin" --freq 1e9 --clock-source 'external' --sync 'pps' --const -g 70 --offset 0 -m 0.8
```

### Calibration USRPs (Tile 3 and 4)

The following script is run, with the settings in `cal-settings.yml`:

```sh
python3 usrp-cal.py
```

Before this a server is set up at my local PC `python3 sync-server.py 1`. To start the timing at all USRPs at the same time.
