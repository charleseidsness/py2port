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
This module provides classes and functions that can be used to calculate the 
LogFuency response of a linear circuit using two port analysis.

Each device is a two port linear-black box that can be connected in series
with other twoport devices to create new two port devices. A one-port device
can be turned into a two-port device in either a series or shunt configuration.

      I1                 I2
     ----> .----------. ---->
    o------|          |-------o
   V1      |          |      V2
           |          |
    o------|          |-------o
           '----------'

Refer to High-Speed Signal Propigation by Howard Johnson, Appendix C or 
Wikipedia <http://en.wikipedia.org/wiki/Two_port> for more details on two-port
analysis.

Functions:
Shunt -- create a new TwoPort Device from a one-port device in parallel
Series -- create a new TwoPort Device from a one-port device in series

Devices:
W -- Lossy T-Line Model
T -- Lossless T-Line Model

"""

from . import oneport
from . import units
from . import freq
from .plot import *

import numpy
import numpy.linalg

def divide(x,y):
	z = x/y
	z[numpy.isnan(z)] = 1e18
	return z

class TwoPort:
	"""
	TwoPort Base Device, not useful on its own but is used to build
	real device models (via inheritance).
	
	Example:
	>>> x = TwoPort()
	>>> x.A(freq.LogF('100Hz', '1000Hz', 2))[1,1,1]
	4.0
	"""
	
	def __init__(self):
		pass
	
	def __mul__(self, a):
		"""
		Add a OnePort Device in Series.
			___
		o--|___|--o
			 Z
		o---------o
		"""
		return self + Series(a)
	
	def __div__(self, a):
		"""
		Add a OnePort Device in Parallel.
		
		o-------o
		    |
		   .-.
		   | |Z
		   '-'
		    |
		o-------o
		"""
		return self + Shunt(a)
	
	def __pow__(self, a):
		"""
		Connect multiple instances of the same device in Series.
		"""
		x = self
		for i in range(0,a):
			x = Connect(x, self)
		return x
	
	def __add__(self, a):
		"""
		Connect two two-port devices together.
		"""
		return Connect(self, a)
	
	def A(self, fc):
		"""
		Returns the device's ABCD Matrix at each LogFuency point
		(complex values).
		
		Arguments:
		fc -- LogFuency class, LogFuencies to calc ABCD at.
		"""
		A = [[0.0*fc.rad + 1, 0.0*fc.rad + 2],
			[0.0*fc.rad + 3, 0.0*fc.rad + 4]]
		return numpy.array(A)
	
	def Zin(self, fc):
		"""
		Returns the device's Open-circuit Input Impedance at each LogFuency 
		point (complex values, Ohms).
		
		Arguments:
		fc -- LogFuency class, LogFuencies to calc Z at.
		"""
		A = self.A(fc)
		return divide(A[0,0],A[1,0])
	
	def Zout(self, fc):
		"""
		Returns the device's Open-circuit Output Impedance at each LogFuency 
		point (complex values, Ohms).
		
		Arguments:
		fc -- LogFuency class, LogFuencies to calc Z at.
		"""
		
		# Maybe there's a faster way to impliment this?
		a = numpy.ndarray((2,2,len(fc)), dtype=numpy.complex)
		A = self.A(fc)
		for i in range(0,len(fc)):
			a[:,:,i] = numpy.linalg.inv(A[:,:,i])
		return -divide(a[0,0],a[1,0])
	
	def Gf(self, fc):
		"""
		Returns the device's Forward Voltage Gain at each LogFuency 
		point (complex values).
		
		Arguments:
		fc -- LogFuency class, LogFuencies to calc G at.
		"""
		A = self.A(fc)
		return divide(1,A[0,0])
	
	def Gr(self, fc):
		"""
		Returns the device's Reverse Voltage Gain at each LogFuency 
		point (complex values).
		
		Arguments:
		fc -- LogFuency class, LogFuencies to calc G at.
		"""
		
		# Maybe there's a faster way to impliment this?
		a = numpy.ndarray((2,2,len(fc)), dtype=numpy.complex)
		A = self.A(fc)
		for i in range(0,len(fc)):
			a[:,:,i] = numpy.linalg.inv(A[:,:,i])
		return -divide(1,a[0,0])
	
	def plotZout(self, fc, title='None'):
		"""
		Plot Output Impedance vs. LogFuency for a Two-Port Device.
		
		MUST RUN plot.show() TO SEE THE PLOTS.
		
		Note: If running from a command line put in interactive mode with
		the plot.live() command.
		
		Arguments:
		fc -- LogFuency class
		title -- Plot heading -- default = 'None'
		
		Example:
		>>> c = Shunt(oneport.C('100nF'))
		>>> r = Series(oneport.R(10))
		>>> (c+r).plotZout(freq.LogF('10kHz', '1GHz', 100), 'Zout Example')
		"""
		plot.addZoutPlot(fc.hz, self.Zout(fc), title)
	
	def plotZin(self, fc, title='None'):
		"""
		Plot Input Impedance vs. LogFuency for a Two-Port Device.
		
		MUST RUN plot.show() TO SEE THE PLOTS.
		
		Note: If running from a command line put in interactive mode with
		the plot.live() command.
		
		Arguments:
		fc -- LogFuency class
		title -- Plot heading -- default = 'None'
		
		Example:
		>>> c = Shunt(oneport.C('100nF'))
		>>> r = Series(oneport.R(10))
		>>> (c+r).plotZin(freq.LogF('10kHz', '1GHz', 100), 'Zin Example')
		"""
		plot.addZinPlot(fc.hz, self.Zin(fc), title)
	
	def plotGf(self, fc, title='None'):
		"""
		Plot Forward Gain vs. LogFuency for a Two-Port Device.
		
		MUST RUN plot.show() TO SEE THE PLOTS.
		
		Note: If running from a command line put in interactive mode with
		the plot.live() command.
		
		Arguments:
		fc -- LogFuency class
		title -- Plot heading -- default = 'None'
		
		Example:
		>>> c = Shunt(oneport.C('100nF'))
		>>> r = Series(oneport.R(10))
		>>> (c+r).plotGf(freq.LogF('10kHz', '1GHz', 100), 'Gf Example')
		"""
		plot.addGfPlot(fc.hz, self.Gf(fc), title)
	
	def plotGr(self, fc, title='None'):
		"""
		Plot Reverse Gain vs. LogFuency for a Two-Port Device.
		
		MUST RUN plot.show() TO SEE THE PLOTS.
		
		Note: If running from a command line put in interactive mode with
		the plot.live() command.
		
		Arguments:
		fc -- LogFuency class
		title -- Plot heading -- default = 'None'
		
		Example:
		>>> c = Shunt(oneport.C('100nF'))
		>>> r = Series(oneport.R(10))
		>>> (c+r).plotGr(freq.LogF('10kHz', '1GHz', 100), 'Gr Example')
		"""
		plot.addGrPlot(fc.hz, self.Gr(fc), title)

class Shunt(TwoPort):
	"""
	Convert a One-Port Device in to a Two-Port Device connected in 
	parallel, i.e.:
	
		o-------o
		    |
		   .-.
		   | |Z
		   '-'
		    |
		o-------o
	
	Example:
	>>> x = Shunt(oneport.C('10u'))
	>>> y = Shunt(oneport.L('10n'))
	>>> z = (x+y)
	>>> z.Zin(freq.LogF('10Hz', '1000Hz', 2))
	array([ 0. +6.28318531e-07j,  0. +2.91639630e-06j,  0. +1.35367149e-05j,
		0. +6.28321011e-05j])
	"""
	
	def __init__(self, device):
		"""
		Arguments:
		device -- one-port device
		"""
		TwoPort.__init__(self)
		self.Z = device
	
	def A(self, fc):		
		A = [[numpy.ones(len(fc)), numpy.zeros(len(fc))],
			[divide(1,self.Z.Z(fc)), numpy.ones(len(fc))]]
		return numpy.array(A)

class Series(TwoPort):
	"""
	Convert a One-Port Device in to a Two-Port Device connected in 
	series, i.e.:
			___
		o--|___|--o
			 Z
		o---------o
	
	Example:
	>>> w = Shunt(oneport.R('0.00001'))
	>>> x = Series(oneport.C('10u'))
	>>> y = Series(oneport.L('10n'))	
	>>> z = (x+y+w)
	>>> z.Zin(freq.LogF('10Hz', '1000Hz', 2))
	array([  1.00000000e-05-1591.54943029j,   1.00000000e-05 -342.88892757j,
		 1.00000000e-05  -73.87316713j,   1.00000000e-05  -15.91543148j])
	"""
	
	def __init__(self, device):
		"""
		Arguments:
		device -- one-port device
		"""
		TwoPort.__init__(self)
		self.Z = device
	
	def A(self, fc):
		A = [[numpy.ones(len(fc)), self.Z.Z(fc)],
			[numpy.zeros(len(fc)), numpy.ones(len(fc))]]
		return numpy.array(A)

class Connect(TwoPort):
	"""
	Connects two TwoPort Devices in series.
	
	Example:
	>>> x = Shunt(oneport.C('10u'))
	>>> y = Shunt(oneport.L('10n'))
	>>> z = (x+y)
	>>> z.Zin(freq.LogF('10Hz', '1000Hz', 2))
	array([ 0. +6.28318531e-07j,  0. +2.91639630e-06j,  0. +1.35367149e-05j,
		0. +6.28321011e-05j])
	"""
	
	def __init__(self, a, b):
		"""
		Arguments:
		a -- first device
		b -- second device
		"""
		TwoPort.__init__(self)
		self.a = a
		self.b = b
	
	def A(self, fc):
		# Maybe there's a faster way to impliment this?
		a = numpy.ndarray((2,2,len(fc)), dtype=numpy.complex)
		A = self.a.A(fc)
		B = self.b.A(fc)
		for i in range(0,len(fc)):
			a[:,:,i] = numpy.dot(A[:,:,i],B[:,:,i])
		return a

class W(TwoPort):
	"""
	Lossy Transmission-Line Model
	
	A W-Element-like model with dielectric and skin-effect losses. The
	arguments can be calculated using a tool like TNT (MMTL) which is
	open source and can be found here: <http://mmtl.sourceforge.net/>
	
	Example:
	>>> t = W(1, 6.35011e-7, 5.10343e-11, 0.0, 0.0, 0.0, 0.0)
	>>> r = Shunt(oneport.R(10))
	>>> (t+r).A(freq.LogF('10kHz','100kHz',1))[0,0]
	array([ 1.+0.00010134j])
	>>> (t+r).plotGf(freq.LogF('10kHz','10GHz',100), 'Lossy-TLine Example')
	"""
	
	def __init__(self, length, L, C, R0=0.0, G0=0.0, Rs=0.0, Gd=0.0):
		"""
		Arguments:
		length -- length of T-Line (inches)
		L -- inductance per meter (H/m)
		C -- capacitance per meter (C/m)
		R0 -- series resistance per meter (Ohm/m) -- default = 0
		G0 -- parallel conductance per meter (S/m) -- default = 0
		Rs -- skin effect resistance (Ohm/(m*sqrt(Hz)) -- default = 0
		Gd -- dielectric loss conductance (S/(m*Hz) -- default = 0
		"""
		
		TwoPort.__init__(self)
		self.length = units.float(length)/39.3700787
		self.L = units.float(L)
		self.C = units.float(C)
		self.R0 = units.float(R0)
		self.G0 = units.float(G0)
		self.Rs = units.float(Rs)
		self.Gd = units.float(Gd)		
	
	def A(self, fc):
		# skin effect
		R = self.R0*numpy.sign(fc.rad)
		R += numpy.sqrt(fc.hz+0.0j)*(1+1j)*self.Rs
		# dielectric loss
		G = self.G0*numpy.sign(fc.rad)
		G += divide(fc.hz,(numpy.sqrt(1+(fc.hz)**2)+0.0j))*self.Gd
		# characteristic impedance
		Zc = numpy.sqrt(divide((1j*fc.rad*self.L + R),(1j*fc.rad*self.C + G)))
		# propigation coefficient
		y = numpy.sqrt((1j*fc.rad*self.L + R)*(1j*fc.rad*self.C + G))
		y *= numpy.sign(fc.rad)
		# transmission coefficient
		H = numpy.exp(-self.length*y)		
		# ABDC Matirx		
		A = [[(divide(1,H) + H)/2, Zc*(divide(1,H) - H)/2],
			[(1/Zc)*((divide(1,H) - H)/2), (divide(1,H) + H)/2]]
		return numpy.array(A)

class T(TwoPort):
	"""
	Lossless Transmission-Line Model
	
	>>> t = T(1, 100)
	>>> r = Shunt(oneport.R(10))
	>>> (t+r).A(freq.LogF('10kHz','100kHz',1))[0,0]
	array([ 1.+0.00011039j])
	>>> (t+r).plotGf(freq.LogF('10kHz','10GHz',100), 'Lossless-TLine Example')
	"""
	
	def __init__(self, length, Zc, er=4.3):
		"""
		Arguments:
		length -- length of T-Line (inches)
		Zc -- characteristic impedance (Ohms)
		er -- permitivity (unitless) -- default = 4.3
		"""
		
		TwoPort.__init__(self)
		self.length = units.float(length)
		self.Zc = units.float(Zc)
		self.er = er		
	
	def A(self, fc):
		# characteristic impedance
		Zc = self.Zc
		# propigation coefficient
		c = 1.18028527e10 # in/sec
		y = (numpy.sqrt(self.er)/c)*1j*fc.rad
		# transmission coefficient
		H = numpy.exp(-self.length*y)
		# ABDC Matirx
		A = [[(divide(1,H) + H)/2, Zc*(divide(1,H) - H)/2],
			[(1/Zc)*(divide(1,H) - H)/2, (divide(1,H) + H)/2]]
		return numpy.array(A)


if __name__ == '__main__':
	
	import doctest
	doctest.testmod(verbose=False)
	print('Testing Complete')
	plot.show()