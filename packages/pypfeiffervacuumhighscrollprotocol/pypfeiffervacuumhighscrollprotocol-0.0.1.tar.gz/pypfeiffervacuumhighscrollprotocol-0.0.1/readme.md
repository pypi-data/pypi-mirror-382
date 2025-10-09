# pyPfeifferVacuumHighscrollProtocol
### Disclaimer
This software is an independent product and is not developed, maintained, or endorsed by Pfeiffer. 
All trademarks, brand names, and product names referenced in this software are the property of their respective owners.
This software is designed to interface with machines manufactured by Pfeiffer, but it is not affiliated with, authorized by,
or supported by Pfeiffer in any way. Use of this software is at the user's own risk. 
The developers of this software make no warranties, express or implied, regarding compatibility, functionality,
or reliability when used in conjunction with Pfeiffer’s hardware or software.
By using this software, you acknowledge that MPfeiffer is not responsible for any damage, malfunction, or loss resulting from its use.

### Introduction:
The module was developed for use at IPF Dresden as a tool to extract data via *RS485* from
Pfeiffer Vacuum Pumps using the *Pfeiffer Vacuum Protocol*.
The here published module was tested with Pfeiffer Vacuum Highscroll 6 Pumps.<p>
Before working with this software please refer to the documentation of the Pfeiffer Vacuum Protocoll in the manual of :
your device. For example the manual of the Pfeiffer Vacuum Highscroll Pumps:

- https://www.pfeiffer-vacuum.com/filepool/file/scroll-pumps/pu0095bde_d.pdf?referer=2573&detailPdoId=46287&request_locale=en_EN

An uptodate version of the module documented in this readme can be found at the following IPF GitLab repository:<p>
- https://gitlab.ipfdd.de/Henn/pypfeiffervacuumhighscrollprotocol

This repository is based on a GitHub repository by Christopeher M. Pirce 
(https://github.com/electronsandstuff/py-pfeiffer-vacuum-protocol)
If you encounter problems while using this software or have ideas for enhancing it, please feel free 
to contribute to this GitLab repository or get in contact with the auther at henn@ipfdd.de!

### Setup:

#### Connection:
For working with the software the Pfeiffer Vacuum Pump needs to be connected to the controlling computer with 
an adapter to a USB (or other Serial Interface). For this purpose adapters are available by Pfeiffer Vacuum themselves
(Pfeiffer Vacuum order number: PM 061 207 -T). It is also possible to build your one connection cabel, the pin diagram is 
documentated in the original manual (linked above) of the Highscroll 6 pumps.


Please ashure a working connection before using the module! 
A connection to the pump can be detected for example using the device manager and tested using CleverTerm / HyperTerm
or the pyserial libary.

#### Python:
To work with the module use Python 3.10 or newer. The module relies on the following packages that can be installed
using pip.

- enum
- pyserial (To use the Module you need to pass a serial object as parameter.)
  

Locate the pyPfeifferVacuumHighscrollProtocol.py file in the root folder of your python script.
Use the module as in the following:<p>

```
import serial
import logging
import pyPfeifferVacuumHighscrollProtocol as pvhp

ComPort = "COM1"
PumpAddress = 2

# defining serial objekt
ser = serial.Serial()
baudrate = 9200
ser.port = ComPort
ser.timeout = 1

try:
    # Open the serial port with a 1 second timeout
    ser.open()
    if ser.is_open:
        logging.info("serial connection established")
        print("serial connection established")

        # Read the pressure from address 2 and prin t it
        p = pvhp.read_pressure(ser, PumpAdress)
        print("Pressure: {:.3f} bar".format(p))

except Exception:
    logging.error("Error querying the Pfeiffer Vacuum pump!")
    print("Error Error querying the Pfeiffer Vacuum pump!")

```

The module has a build in filter for invalid characters written by C. Pirce. The use of the filter is dokumented 
in the pvp GitHub repository (https://github.com/electronsandstuff/py-pfeiffer-vacuum-protocol)

### Licence
The module is published under BSD 3 Licence
>BSD 3-Clause License
>
>Copyright (c) 2024, Enno Henn, Leibiz Institute of Polymer Reserche Dresden (henn@ipfdd.de)
>All rights reserved.
>
>Redistribution and use in source and binary forms, with or without
>modification, are permitted provided that the following conditions are met:
>
>* Redistributions of source code must retain the above copyright notice, this
>  list of conditions and the following disclaimer.
>
>* Redistributions in binary form must reproduce the above copyright notice,
>  this list of conditions and the following disclaimer in the documentation
>  and/or other materials provided with the distribution.
>
>* Neither the name of the copyright holder nor the names of its
>  contributors may be used to endorse or promote products derived from
>  this software without specific prior written permission.
>
>THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
>AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
>IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
>DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
>FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
>DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
>SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
>CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
>OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
>OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
>"""
