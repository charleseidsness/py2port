#
# Copyright (C) 2008 Cooper Street Innovations Inc.
# Charles Eidsness    <charles@cooper-street.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

"""
This module contains classes and functions that can be used to define,
combine and solve One Port (two-pin) circuits built from One Port devices.

- Connect two devices in InLine using the * operator.
- Connect two devices in parallel using the / operator.
- Connect multiple instances of the same device in InLine using the ** operator.
- Connect multiple instances of the same device in parallel using the // operator.

Devices:

R -- Basic resistor
C -- Basic capacitor
L -- Basic inductor

Cb -- Bypass capacitor with paracitics
Lia -- Inductance between two vias
Lb -- Ferrite Bead Model
Cp -- PWR/GND Plane Pair Model

Examples:

(Note: The ascii schematic's were drawn using AACircuit, if you're interested
you can find it here: <http://www.tech-chat.de/aacircuit.html>)

If running from a Python Shell, run this command to plot as you go
>>> # plot.live() #

1. Simple Bypass Capacitors in Parallel
Note: ESL and ESR are from AVX's SpiCap3 Tool
<http://www.avx.com/spiapps/spicap/spicap3.exe>

>>> C1 = Cb(c='100nF', esl='0.5nH', esr='0.039')
>>> C2 = Cb(c='1uF', esl='1.0nH', esr='0.014')

Four C1's in parallel with six C2's.
>>> cct = (C1//2)/(C2//6)
>>> cct.Z(freq.LogF('10MHz', '100MHz', 2))
array([ 0.01837133+0.02840595j,  0.00966525+0.1012983j ])

>>> cct.plotZ(freq.LogF('10kHz', '1GHz', 100), 'Bypass Example')

2. Impedance of a Power Distribution System from the perpesctive of a Device

   .----------o----------o-------o
   |          |          |
   |          '          |
  --- Plane  --- Clf*2  --- Chf*10
  ---        ---        ---
   |          |          |
   |          |          |
   '----------o----------o-------o

High Frequency Bypass including mounting inductance
>>> Chf = Cb(c='100nF', esl='0.5nH', esr='0.039')
>>> L_via = Lvia('10mil', '62mil', '20mil')
>>> Lhf_mount = L('1nH') # Esitmate of extra mounnting L
>>> Chf = (Chf*L_via*Lhf_mount) # Put them all in parallel

Low Frequency Bypass including mounting inductance
>>> Clf = Cb(c='12uF', esl='1nH', esr='0.045')
>>> Llf_mount = L('3nH') # Esitmate of extra mounnting L
>>> Clf = (Clf*L_via*Llf_mount) # Put them all in parallel

Plane Impedance
>>> Zp = Cp(x='1in', y='1in', X='20in', Y='10in', h='2mil')

Put them all in parallel
>>> Zpds = Zp/(Clf//2)/(Chf//10)

Plot
>>> Zpds.plotZ(freq.LogF('10kHz', '1GHz', 100), 'PDS Example')

3. Impedance of Ferrite Based Pi-Filter from the perspective of a Device

                                ___
  .----------o----------o------|___|---o------------------o
  |          |          |      Zbead   |          |
  |          '          |              |          |
 --- Plane  --- Clf    --- Chf*2      --- Clf    --- Chf*2
 ---        ---        ---            ---        ---
  |          |          |              |          |
  |          |          |              |          |
  '----------o----------o--------------o----------o-------o

Ferrite Model
>>> F = numpy.array([0.0001, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, \
		50, 60, 70, 80, 90, 100, 200, 300, 400, 500, 600, 700, 800, 900, \
		1000, 2000])*1e6
>>> R = [0.35, 0.035, 5, 20, 40, 50, 55, 65, 80, 95, 100, 200, 250, 310, \
		355, 400, 450, 475, 500, 540, 700, 750, 770, 755, 750, 725, 700, \
		675, 670, 400]
>>> X = [0, 40, 50, 80, 100, 110, 120, 140, 145, 150, 155, 220, 250, 275, \
		280, 285, 280, 275, 265, 255, 160, 60, -10, -60, -100, -175, -225, \
		-250, -275, -285]
>>> Zbead = Lb(F, R, X)

High. LogF. Caps including mounting inductance
>>> Chf = Cb(c='100nF', esl='0.5nH', esr='0.039')
>>> L_via = Lvia('10mil', '62mil', '20mil')
>>> Lhf_mount = L('1nH') # Esitmate of extra mounnting L
>>> Chf = (Chf*L_via*Lhf_mount) # Put them all in parallel

Low. LogF. Caps including mounting inductance
>>> Clf = Cb(c='12uF', esl='1nH', esr='0.045')
>>> Llf_mount = L('3nH') # Esitmate of extra mounnting L
>>> Clf = (Clf*L_via*Llf_mount) # Put them all in parallel

Plane Impedance
>>> Zp = Cp(x='1in', y='1in', X='20in', Y='10in', h='2mil')

Put them all together
>>> Zpds = ((Zp/Clf/(Chf//2))*Zbead)/(Clf/(Chf//2))

Plot
>>> Zpds.plotZ(freq.LogF('10kHz', '1GHz', 100), 'Pi-Filter Example')

"""

from . import units
from . import freq
from .plot import *

import numpy
import scipy.interpolate

# --------------------------------------------------------------------------- #

def divide(x,y):
	z = x/y
	z[numpy.isnan(z)] = 1e18
	return z

class OnePort:
	"""
	OnePort Base Device, not useful on its own but is used to build
	real device models (via inheritance).

	Example:
	>>> x = OnePort()
	>>> (x*x).Z(freq.LogF('10Hz', '1000Hz', 2))
	array([ 0.+0.j,  0.+0.j,  0.+0.j,  0.+0.j])
	"""

	def __init__(self):
		pass

	def __mul__(self, a):
		"""
		Connect two Devices in InLine.
		"""
		return InLine(self, a)

	def __div__(self, a):
		"""
		Connect two Devices in Parallel.
		"""
		return Parallel(self, a)

	def __pow__(self, a):
		"""
		Connect multiple instances of the same device in InLine.

		Example:
		>>> y = Cb()
		>>> (y**4).Z(freq.LogF('10kHz','100kHz', 2))
		array([ 0.195-795.77455838j,  0.195 -79.57590075j])
		"""
		x= self
		for i in range(0,a):
			x = InLine(x, self)
		return x

	def __floordiv__(self, a):
		"""
		Connect multiple Devices in Parallel.
		"""
		for i in range(0,a):
			x = Parallel(self, self)
		return x

	def Z(self, fc):
		"""
		Returns the device's impedance at each LogFuency point (complex values).

		Arguments:
		fc -- LogFuency class, LogFuencies to calc Z at.
		"""
		return 0.0*fc.rad + 0.0j*fc.rad

	def plotZ(self, fc, title='None'):
		"""
		Plot impedance vs. LogFuency for a One-Port Device.

		MUST RUN plot.show() TO SEE THE PLOTS.

		Note: If running from a command line put in interactive mode with
		the plot.live() command.

		Arguments:
		fc -- LogFuency class
		title -- Plot heading -- default = 'None'

		Example:
		>>> (C('100nF')).plotZ( \
				freq.LogF('10kHz', '1GHz', 100), 'Capacitor Example')
		"""
		plot.addZPlot(fc.hz, self.Z(fc), title)

class InLine(OnePort):
	"""
	Connects two OnePort Devices in InLine.

	Example:
	>>> x = C('10u')
	>>> y = L('10n')
	>>> z = (x*y)
	>>> z.Z(freq.LogF('10Hz', '1000Hz', 2))
	array([ 0.-1591.54943029j,  0. -342.88892757j,  0.  -73.87316713j,
		0.  -15.91543148j])
	"""

	def __init__(self, a, b):
		"""
		Arguments:
		a -- first device
		b -- second device
		"""
		OnePort.__init__(self)
		self.a = a
		self.b = b

	def Z(self, fc):
		return self.a.Z(fc) + self.b.Z(fc)

class Parallel(OnePort):
	"""
	Connects two OnePort Devices in parallel.

	Example:
	>>> x = C('10u')
	>>> y = L('10n')
	>>> z = (x/y)
	>>> z.Z(freq.LogF('10Hz', '1000Hz', 2))
	array([ 0. +6.28318531e-07j,  0. +2.91639630e-06j,  0. +1.35367149e-05j,
		0. +6.28321011e-05j])
	"""

	def __init__(self, a, b):
		"""
		Arguments:
		a -- first device
		b -- second device
		"""
		OnePort.__init__(self)
		self.a = a
		self.b = b

	def Z(self, fc):
		return divide(1,(divide(1,self.a.Z(fc)) + divide(1,self.b.Z(fc))))

# --------------------------------------------------------------------------- #

class R(OnePort):
	"""
	Resistor Model.

	Example:
	>>> x = R('10M')
	>>> x.Z(freq.LogF('10Hz', '1000Hz', 2))
	array([ 10000000.+0.j,  10000000.+0.j,  10000000.+0.j,  10000000.+0.j])
	"""

	def __init__(self, value=10):
		"""
		Arguments:
		value -- resistance (Ohms) -- default = 10
		"""
		OnePort.__init__(self)
		self.value = units.float(value)

	def Z(self, fc):
		return self.value + fc.rad*0.0j

class C(OnePort):
	"""
	Capacitor Model.

	Example:
	>>> x = C('10u')
	>>> x.Z(freq.LogF('10Hz', '1000Hz', 2))
	array([ 0.-1591.54943092j,  0. -342.88893049j,  0.  -73.87318067j,
		0.  -15.91549431j])
	"""

	def __init__(self, value=10e-9):
		"""
		Arguments:
		value -- capacitance (F) -- default = 10nF
		"""
		OnePort.__init__(self)
		self.value = units.float(value)

	def Z(self, fc):
		return divide(1,(fc.rad*self.value*1j))


class L(OnePort):
	"""
	Inductor Model.

	Example:
	>>> x = L('10u')
	>>> x.Z(freq.LogF('10Hz', '1000Hz', 2))
	array([ 0.+0.00062832j,  0.+0.0029164j ,  0.+0.01353671j,  0.+0.06283185j])
	"""

	def __init__(self, value=10e-6):
		"""
		Arguments:
		value -- inductance (H) -- default = 10uF
		"""
		OnePort.__init__(self)
		self.value = units.float(value)

	def Z(self, fc):
		return fc.rad*self.value*1j

def Cb(c='100nF', esl='0.5nH', esr='0.039'):
	"""
	Creates a Bypass Capacitor Model, including ESL and ESR.

				 C
				||  ESL   ESR
			o---||--UUU--/\/\/\---o
				||

	Arguments:
	c -- capacitance
	esl -- effective InLine inductance
	esr -- effective InLine resistance

	Example:
	>>> Cb('100nF', '1nH', '0.001Ohm').Z(freq.LogF('10MHz', '100MHz', 2))
	array([ 0.001-0.09632309j,  0.001+0.61240304j])
	"""
	return (C(c)*L(esl)*R(esr))

def Lvia(d='12mil', h='50mil', s='100mil'):
	"""
	Creates a Via Inductance Model for a pair of vias.

	- Based on <http://www.sigcon.com/Pubs/news/6_08.htm>
		by Howard Johnson

	Arguments:
	d -- via drill diameter (inches) -- default = 12mil
	h -- length of via between layers used (inches) -- default = 50mil
	s -- distance from via to via (inches) -- default = 100mil

	Example:
	>>> Lvia('10mil', '62mil', '20mil').Z(freq.LogF('10MHz', '100MHz', 2))
	array([ 0.+0.0548682j ,  0.+0.54868201j])
	"""

	d = units.float(d)
	h = units.float(h)
	s = units.float(s)
	l = 5.08*2*h*(numpy.log(2*s/d))*1e-9
	return L(l)

class Lb(OnePort):
	"""
	Ferrite Bead Model.

	Due to the difficulty modeling a ferrite using standard devices this model
	uses linear interpolation and the points on the ferrite's impedance curve.
	To build a model enter a set of data points	from the ferrite's impedance
	curve (should be in a spec sheet). The model will fill in the missing
	points using linear inetrpolation so make sure you provide enough points at
	non-linear parts of the curve.

	Example (BLM18EG601SV18) based filter:

                  r
              .-/\/\/\---.
              |  ___     |
            o-o-|___|----o---o---.
   Impedance      l      |   |   |
      ----->            --- --- ---
                      c --- --- ---
            o            |   |   |
            |            |   |   |
           ===          === === ===
           GND          GND GND GND

	>>> f = numpy.array([0.0001, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, \
			50, 60, 70, 80, 90, 100, 200, 300, 400, 500, 600, 700, 800, 900, \
			1000, 2000])*1e6
	>>> r = [0.35, 0.035, 5, 20, 40, 50, 55, 65, 80, 95, 100, 200, 250, 310, \
			355, 400, 450, 475, 500, 540, 700, 750, 770, 755, 750, 725, 700, \
			675, 670, 400]
	>>> x = [0, 40, 50, 80, 100, 110, 120, 140, 145, 150, 155, 220, 250, 275, \
			280, 285, 280, 275, 265, 255, 160, 60, -10, -60, -100, -175, -225, \
			-250, -275, -285]
	>>> l = Lb(f, r, x)
	>>> c = Cb('100nF', '1nH', '0.001Ohm')
	>>> r = R(10)
	>>> cct = ((l/r)*(c//3))
	>>> cct.Z(freq.LogF('10kHz', '100kHz', 2))
	array([ 0.34989075-79.20805119j,  1.57330666 -4.69355357j])
	>>> cct.plotZ(freq.LogF('10kHz', '1GHz', 100), 'Ferrite Example')
	"""

	def __init__(self, LogF=[0,10e9], R=[1,1], X=[1,1]):
		"""
		Arguments:
		LogF -- array/list of LogFuency points (Hz)
		R -- Resistance at each LogFuency point (Ohms)
		X -- Reactance at each LogFuency point (H)
		"""
		OnePort.__init__(self)

		if (len(LogF) != len(R)) or (len(LogF) != len(X)):
			raise RuntimeError('length of all arguments must match')

		LogF = units.floatList1D(LogF)
		R = units.floatList1D(R)
		X = units.floatList1D(X)

		self.R = f = scipy.interpolate.interp1d(LogF, R)
		self.X = f = scipy.interpolate.interp1d(LogF, X)

	def Z(self, fc):
		return self.R(fc.hz) + self.X(fc.hz)*1j

class Cp(OnePort):
	"""
	Parallel Plane Model

	This model is based on the paper "Accuracy Considerations of Power-Ground
	Plane Models" by Istvan Novak, you should be able to find it here:
	<http://home.att.net/~istvan.novak/papers/epep99_slides.pdf>.

	It provides a model for a rectangular PWR/GND plane structure in a PCB,
	not taking into account any plane cut-outs, vias, etc...

	Example:
	>>> x = Cp(1, 1, 20, 10, 0.002)
	>>> x.Z(freq.LogF('100MHz', '1GHz', 2))
	array([ 0.+0.05556665j,  0.-0.1733445j ])
	>>> x.plotZ(freq.LogF('10kHz', '1GHz', 100), 'Plane Example')
	"""

	def __init__(self, x=1, y=1, X=20, Y=10, h=0.002, er=4.7, N=20, M=20):
		"""
		 +--- X -----+
		+.-----------.
		||           |
		||       o   |+
		Y|     point ||
		||           |y
		||           ||
		||           ||
		+'-----------'+
		+-- x --+

		Arguments:
		x -- x location of test point (inch) -- default = 1
		y -- y location of test point (inch) -- default = 1
		X -- X dimmension of plane (inch) -- default = 20
		Y -- Y dimmension of plane (inch) -- default = 10
		h -- distance between planes (inch) -- default = 0.002
		er -- permitivity of the dielectric -- deafault = 4.7
		N -- size of bedspring grid in X dimmension -- default = 20
		M -- size of bedspring grid in Y dimmension -- default = 20
		"""

		self.x = units.float(x)
		self.y = units.float(y)
		self.X = units.float(X)
		self.Y = units.float(Y)
		self.h = units.float(h)

		self.M = M
		self.N = N

		# Plane capacitance
		e0 = 2.24896371e-13 # F/in
		self.Cp = e0 * er * ((self.X * self.Y) / self.h)

		# Propigation time accross plane
		c = 1.18028527e10 # in/sec
		v = c / numpy.sqrt(er)
		self.tpdx = self.X / v
		self.tpdy = self.Y / v

		def Cs(p, q, r):
			return numpy.cos(numpy.pi*p*q/r)

		self.A = numpy.ndarray((M,N), dtype=numpy.double)
		for m in range(0,self.M):
			for n in range(0,self.N):
				if (m == 0) and (n == 0):
					a = 1
				elif ((m == 0) and (n > 0)) or ((n == 0) and (m > 0)):
					a = 2
				else:
					a = 4
				self.A[m,n] = a*Cs(m,self.x,self.X)**2*Cs(n,self.y,self.Y)**2

	def Z(self, fc):

		def Phs(i, w, tpd):
			return ((numpy.pi*i)/(w*tpd))**2

		a = numpy.zeros(len(fc))
		for m in range(0,self.M):
			for n in range(0,self.N):
				a += (self.A[m,n] /
						(1 - Phs(m, fc.rad, self.tpdx) -
				Phs(n, fc.rad, self.tpdy)))

		return (divide(1,(fc.rad*self.Cp*1j)))*a

# --------------------------------------------------------------------------- #

if __name__ == '__main__':

	import doctest
	doctest.testmod(verbose=False)
	print('Testing Complete')
	plot.show()
