#!/usr/bin/python
"""
Gain of Ferrite Based Pi-Filter from the perspective of a Device

                                ___
  .----------o----------o------|___|---o------------------o
  |          |          |      Zbead   |          |
  |          '          |              |          |
 --- Plane  --- Clf    --- Chf*2      --- Clf    --- Chf*2
 ---        ---        ---            ---        ---
  |          |          |              |          |
  |          |          |              |          |
  '----------o----------o--------------o----------o-------o
"""

import py2port
import numpy

# Ferrite Bead Model
F = numpy.array([0.0001, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40,
		50, 60, 70, 80, 90, 100, 200, 300, 400, 500, 600, 700, 800, 900,
		1000, 2000])*1e6
R = [0.35, 0.035, 5, 20, 40, 50, 55, 65, 80, 95, 100, 200, 250, 310,
		355, 400, 450, 475, 500, 540, 700, 750, 770, 755, 750, 725, 700,
		675, 670, 400]
X = [0, 40, 50, 80, 100, 110, 120, 140, 145, 150, 155, 220, 250, 275,
		280, 285, 280, 275, 265, 255, 160, 60, -10, -60, -100, -175, -225,
		-250, -275, -285]
Zbead = py2port.Lb(F, R, X)

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

# Create Two-Port Elements for the structures on the left
# and right of the Bead.
Aleft = py2port.Shunt(Zp/Clf/(Chf//2))
Aright = py2port.Shunt(Clf/(Chf//2))

# Two-Port Element for the Bead
Abead = py2port.Series(Zbead)

# Connect them all together
Afilter = Aleft + Abead + Aright

# Plot the result
Afilter.plotGf(py2port.LogF('10kHz', '1GHz', 100), 'Pi-Filter Example')
Afilter.plotGr(py2port.LogF('10kHz', '1GHz', 100), 'Pi-Filter Example')
Afilter.plotZin(py2port.LogF('10kHz', '1GHz', 100), 'Pi-Filter Example')
Afilter.plotZout(py2port.LogF('10kHz', '1GHz', 100), 'Pi-Filter Example')

# Show the plots
py2port.plot.show()

