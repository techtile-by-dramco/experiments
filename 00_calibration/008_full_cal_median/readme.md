# Repeated simple setup 003

Same as 002, only now the loopback is done manually (through cable no LO leakage through RF switch) and now the USRPs are both driven by the PPS and 10MHz of the same octoclock at adjacent ports (ie without phase diff).

This folder contains the files to repeatedly run the `usrp-cal` python script to check the phase diff between 2 USRPs.

There are two options:
1. run `usrp-cal-while.py` which in a loop executes the code
2. run `usrp-cal.sh` which repeatedly calls `usrp-cal.py`.

The following window can be replicated by adding the following to the command setting in Windows Terminal:

```json
 "command": 
            {
                "action": "multipleActions",
                "actions": 
                [
                    {
                        "action": "newTab",
                        "profile": "Ubuntu",
                        "tabTitle": "EXP1",
                        "commandline":"ssh techtile@192.108.0.1"
                    },
                    {
                        "action": "splitPane",
                        "profile": "Ubuntu",
                        "size": 0.66,
                        "split": "right",
                        "tabTitle": "T02",
                        "commandline": "ssh techtile@192.108.0.1"
                    },
                    {
                        "action": "splitPane",
                        "profile": "Ubuntu",
                        "size": 0.5,
                        "split": "right",
                        "tabTitle": "T0",
                        "commandline": "ssh techtile@192.108.0.1"
                    },
                    {
                        "action": "splitPane",
                        "profile": "Command Prompt",
                        "size": 0.5,
                        "split": "up",
                        "tabTitle": "T0",
                        "startingDirectory": "C:/Users/Calle/OneDrive/Documenten/GitHub/experiments/00_calibration/003_repeated_setup",
                        "commandline": "python sync-server.py 2 2"
                    }
                    ,
                    {
                        "action": "splitPane",
                        "profile": "Command Prompt",
                        "size": 0.5,
                        "split": "vertical",
                        "tabTitle": "T0",
                        "startingDirectory": "C:/Users/Calle/OneDrive/Documenten/GitHub/experiments/00_calibration/003_repeated_setup",
                        "commandline": "python meas-phase-scope.py"
                    }
                ]
            },
            "name": "Create Exp 002 Layout"
        }, ...
```
![image](https://github.com/techtile-by-dramco/experiments/assets/8626571/7ebfb2bf-89e2-4532-8864-b87ea08126e1)

### Settings T02
```
~/experiments/00_calibration/002_repeated_setup $ uhd_siggen --args "mode_n=integer" --freq 1e9 --clock-source 'external' --sync 'pps' --const -g 70 --offset 0 -m 0.8
```

### Settings T03 and T04
```
~/experiments/00_calibration/002_repeated_setup $ ./usrp-cal.sh
```

