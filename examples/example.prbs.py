#!/usr/bin/python
"""  
PRBS driving a Lossy T-Line.
"""

import py2port

# Input waveform
vi = py2port.PRBS(bits=50, v1=-1, v2=1, tb='10ns', tr='1ns', tj='100ps')

# Transmission Line (approx 111Ohms) with Source Termination
cct = py2port.Series(py2port.R('100Ohms'))
cct += py2port.W(10, 6.35011e-7, 5.10343e-11, 0.0, 0.0, 0.0, 0.0)
vo = vi >> cct

# Plot the Results
vi.plotVEye('PRBS In')
vo.plotVEye('PRBS Out')
vi.plotI('PRBS In')

# Show the plot
py2port.plot.show()
