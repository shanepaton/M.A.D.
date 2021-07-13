# M.A.D.
The source code for the Mounted Assistant Device or M.A.D.

## Requirements
### Hardware:
- 1x Raspberry Pi
- 1x Passive Buzzer
- 4x Push Buttons
- 1x I2C 1602 Charecter LCD
- 14x Wires
- ( Optional ) USB Flash Drive for BrewSoft

### Software
- Python 3.7.3
- M.A.D. Source Code
- ( Python ) RPLCD
- ( APT ) python-smbus

## Setting Up
### GPIO
The I2C Screen should be connected to:
```
5V : 5V
GND: GND
SDA: SDA
SDL: SDL
```
The Passive Buzzer should be connected to:
```
IN : GPIO 23
OUT: GND
```
The Home Button should be connected to:
```
IN : GPIO 16
OUT: GND
```
The Left Menu Button should be connected to:
```
IN : GPIO 21
OUT: GND
```
The Right Menu Button should be connected to:
```
IN : GPIO 22
OUT: GND
```

The Select Button should be connected to:
```
IN : GPIO 22
OUT: GND
```

### Setup Python Libraries
```console
pi@raspberrypi $ sudo pip install RPLCD
pi@raspberrypi $ sudo apt-get install python-smbus
```

### Starting the software
Extract the source code from the zip file then run by using the command:
```console
pi@raspberrypi $ python3 mad.py
```
The software should be running and the screen should be working.
