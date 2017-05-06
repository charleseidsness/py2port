#!/usr/bin/python
"""
Impedance of a Power Distribution System from the perpesctive of a Device.
Includes two types of bypass capacitors, PCB plane impedance, via
inductance, and device pin paracitics, and one device decouplng.
                             ___     ___
    .--------o--------o-----|___|----UUU----o----o
    |        |        |      Rpin   Lpin    |
    |        |        |                     |
   --- Zp   --- Clf  --- Chf               ---
   ---      ---      ---                   ---Cdie
    |        |        |                     |
    |        |        |      ___     ___    |
    '--------o--------o-----|___|----UUU----o----o
                             Rpin   Lpin
"""

import py2port
  

# High Frequency Bypass including mounting inductance
Chf = py2port.Cb(c='100nF', esl='0.5nH', esr='0.039')
Lhf_via = py2port.Lvia('10mil', '62mil', '20mil')
Lhf_mount = py2port.L('1nH') # Esitmate of extra mounnting L
Chf = (Chf*Lhf_via*Lhf_mount) # Put them all in parallel

# Low. Frequency Bypass including mounting inductance
Clf = py2port.Cb(c='12uF', esl='1nH', esr='0.045')
Llf_via = py2port.Lvia('10mil', '62mil', '20mil')
Llf_mount = py2port.L('3nH') # Esitmate of extra mounnting L
Clf = (Clf*Llf_via*Llf_mount) # Put them all in parallel

# PCB Parallel Plane Impedance
Zp = py2port.Cp(x='1in', y='1in', X='20in', Y='10in', h='2mil')

# Put them all in parallel
Zpds = Zp/(Clf//2)/(Chf//10)

# Pin Paracitics
LRpin = py2port.R('0.003') * py2port.L('0.5nH')
Cdie = py2port.C('10pF')

# Put it all together
Zpds = (Zpds * LRpin**2)/Cdie

# Plot the result
Zpds.plotZ(py2port.LogF('10kHz', '1GHz', 100), 'PDS Example')

# Show the plot
py2port.plot.show()
