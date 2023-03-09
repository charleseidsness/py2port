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
This module provides classes and functions that can be used drive time
domain voltage signals into a twoport network and calculate the input
current and output voltage.

Waveforms:
Gauss -- Arbitrary digital signal with gaussian edges and jitter
Clock -- Clock with gaussian edges and jitter
PRBS -- Psuedo-Random Bit Sequence with gaussian edges and jitter

Examples:

1. 100MHz Clock driving a Lossy T-Line

>>> Vi = Clock(periods=5, v1=0, v2=1, tb='10ns', tr='1ns', tj='100ps')
>>> x = twoport.W(10, 6.35011e-7, 5.10343e-11, 0.0, 0.0, 0.0, 0.0)
>>> x = twoport.Series(oneport.R('100Ohms')) + x
>>> Vo = Vi >> x
>>> Vi.plotV('Clock In')
>>> Vi.plotI('Clock In')
>>> Vo.plotV('Clock Out')

2. PRBS driving a Lossless T-Line

>>> Vi = PRBS(bits=5, v1=0, v2=1, tb='10ns', tr='1ns', tj='100ps')
>>> x = twoport.T(10, 111)
>>> x = twoport.Series(oneport.R('100Ohms')) + x
>>> Vo = Vi >> x
>>> Vi.plotV('PRBS In')
>>> Vi.plotI('PRBS In')
>>> Vo.plotV('PRBS Out')

"""

import numpy
import scipy.special
import pylab
import random

from . import units
from .plot import *
from . import oneport
from . import twoport
from . import freq

def _rfft(time, data):
	ts = time[1] - time[0]
	X = numpy.fft.rfft(data.astype(numpy.double))[1:-1]/len(time)
	f = freq.Freq(numpy.fft.fftfreq(len(data), d=ts)[:len(X)])
	return f, X

def _fft(time, data):
	ts = time[1] - time[0]
	X = numpy.fft.fft(data.astype(numpy.double), n=len(time))
	f = freq.Freq(numpy.fft.fftfreq(len(time), d=ts))
	return f, X

def _ifft(time, data):
	return numpy.fft.ifft(data, n=len(time))

def _gauss(v1, v2, td, tr, tn):	
	tx = (tr/0.672)*0.281*2;
	tx = (tn - (tx/0.281)*0.672-td)/tx
	vo = scipy.special.erf(tx)	
	return 0.5*(v2-v1)*(1+vo)

def _eye(tn, tb, tr):	
	tb = units.float(tb)
	tr = units.float(tr)
	return (tn-2*tr)%tb

class Waveform:
	"""
	Voltage Waveform base device, not too useful on its own but can be used to
	build more useful Waveforms (via inheritance).
	"""
	
	def __init__(self, time, voltage, tb, tr):
		"""
		Arguments:
		time -- array of time values (seconds)
		voltage -- array of voltage values (volts)
		tb -- width of single bit (seconds), used for plot formatting, doesn't
			have to be exact
		tr -- rise/fall times (seconds), used for plot formatting, doesn't
			have to be exact
		"""
		if len(time) != len(voltage):
			raise RunetimeError('Time and voltage arrays must be same size')
		self.time = time
		self.voltage = voltage
		self.current = numpy.zeros(len(time))
		self.tb = tb
		self.tr = tr
	
	def plotV(self, title='None'):
		"""
		Plot Waveform Voltage
		
		MUST RUN plot.show() TO SEE THE PLOTS.
		
		Note: If running from a command line put in interactive mode with
		the plot.live() command.
		
		Arguments:
		title -- Plot heading -- default = 'None'		
		"""
		plot.addVTPlot(self.time, self.voltage, title)
	
	def plotVEye(self, title='None'):
		"""
		Plot Waveform Voltage Eye Diagram
		
		MUST RUN plot.show() TO SEE THE PLOTS.
		
		Note: If running from a command line put in interactive mode with
		the plot.live() command.
		
		Arguments:
		title -- Plot heading -- default = 'None'		
		"""
		plot.addVTPlot(_eye(self.time, self.tb, self.tr), self.voltage, 
				title, 'o')
	
	def plotI(self, title='None'):
		"""
		Plot Waveform Current
		
		MUST RUN plot.show() TO SEE THE PLOTS.
		
		Note: If running from a command line put in interactive mode with
		the plot.live() command.
		
		Arguments:
		title -- Plot heading -- default = 'None'		
		"""
		plot.addITPlot(self.time, self.current, title)		
	
	def plotVSpectrum(self, title='None'):
		"""
		Plot Waveform Voltage in the Frequency Domain
		
		MUST RUN plot.show() TO SEE THE PLOTS.
		
		Note: If running from a command line put in interactive mode with
		the plot.live() command.
		
		Arguments:
		title -- Plot heading -- default = 'None'		
		"""
		f, V = _rfft(self.time, self.voltage)
		plot.addVFPlot(f.hz, V, title)
	
	def plotISpectrum(self, title='None'):
		"""
		Plot Waveform Current in the Frequency Domain
		
		MUST RUN plot.show() TO SEE THE PLOTS.
		
		Note: If running from a command line put in interactive mode with
		the plot.live() command.
		
		Arguments:
		title -- Plot heading -- default = 'None'		
		"""
		f, I = _rfft(self.time, self.current)
		plot.addIFPlot(f.hz, I, title)
	
	def __rshift__(self, device):
		"""
		Drives a waveform into a two-port device.
		"""
		
		# Add 2*tb buffers at each end to mask effects of retangular window
		
		ts = self.time[1]-self.time[0]
		#~ tb = 2*int(self.tb/(self.time[1]-self.time[0]))
		tb = len(self.time)
		time = numpy.arange(self.time[0]-tb*ts, self.time[-1]+tb*ts, ts)
		
		voltage = numpy.zeros(len(time))
		
		# pad with
		voltage[0:tb] = self.voltage[0]
		voltage[-tb-1:-1] = self.voltage[-1]
		voltage[tb:-tb] = self.voltage
		
		f, Vi = _fft(time, voltage)
		
		# Calculate Input Current
		Zi = device.Zin(f)
		Ii = Vi/Zi
		self.current = _ifft(time, Ii)[tb:-tb]
		
		# Calculate Output Voltage
		A = device.Gf(f)
		Vo = Vi*A
		vo = _ifft(time, Vo)
			
		return Waveform(time[tb:-tb], vo[tb:-tb], self.tb, self.tr)

class Gauss(Waveform):
	"""
	Voltage waveform with Gaussian Edges, based on Appendix B of 
	"High-Speed Digital Design" by Johnson and Graham
	
	This waveform should represent a squarewave driven through a set of
	low-pass filters, like most digital logic driven into the LRC paracitics
	of a pin.
	
	Example:
	>>> Vi = Gauss(states=[0,1,0], v1=0, v2=1, tb=10e-9, tr=1e-9, tj=0)
	>>> print Vi.voltage[1200]
	0.5
	>>> Vi.plotV('Gauss Test')	
	"""

	def __init__(self, states=[0,1,0], v1=0, v2=1, tb=10e-9, tr=1e-9, 
			tj=10e-12, resolution = 1e3):
		"""
		Arguments:
		states -- list of digital states
		v1 -- voltage level in in state "0" (volt)
		v2 -- voltage level in in state "1" (volt)
		tb -- width of single bit (seconds)
		tr -- rise/fall times -- 20%-80% -- (seconds)
		tj -- jitter -- standard deviation -- (seconds)
		resolution -- time points per bit
		"""
		
		v1 = units.float(v1)
		v2 = units.float(v2)
		tb = units.float(tb)
		tr = units.float(tr)
		tj = units.float(tj)
		
		length = len(states)*tb
		time = numpy.arange(0.0, length, tb/resolution)
		voltage = numpy.zeros(len(time))
		
		state0 = states[0]
		td = -length
		
		if state0 == 0:
			v1, v2 = v2, v1
		
		for i in range(0,len(time)):
			
			tn = time[i]
			state = states[int(i/resolution)]
			
			if state0 < state:
				state0 = state
				td = tn + random.gauss(tj*6, tj)
				v1, v2 = v2, v1			
			if state0 > state:
				state0 = state
				td = tn + random.gauss(tj*6, tj)
				v1, v2 = v2, v1
				
			voltage[i] = v1 + _gauss(v1, v2, td, tr, tn)
	
		time = time-tj*6
		Waveform.__init__(self, time, voltage, tb, tr)

class Clock(Gauss):
	"""
	Voltage Clock Waveform with Gausian Edges (refer to Gauss).
	
	Example:
	>>> Vi = Clock(4, v1=0, v2=1, tb=10e-9, tr=1e-9, tj=0)
	>>> print Vi.voltage[1200]
	0.5
	>>> Vi.plotV('Clock Test')
	"""
	
	def __init__(self, periods=8, v1=0, v2=1, tb=10e-9, tr=1e-9, tj=10e-12, 
			resolution = 1e3):
		"""
		Arguments:
		periods -- number of clock periods
		v1 -- voltage level in in state "0" (volt)
		v2 -- voltage level in in state "1" (volt)
		tb -- width of single bit (seconds)
		tr -- rise/fall times -- 20%-80% -- (seconds)
		tj -- jitter -- standard deviation -- (seconds)
		resolution -- time points per bit
		"""
		
		states = numpy.zeros(periods*2)
		for i in range(0,periods*2):
			if i%2 == 1:
				states[i] = 1
		
		Gauss.__init__(self, states, v1, v2, tb, tr, tj, resolution)
		
		
class PRBS(Gauss):
	"""
	Voltage Pseudo-Random Bit Sequence Waveform with Gausian Edges 
	(refer to Gauss).
	
	Example:
	>>> Vi = PRBS(12, v1=0, v2=1, tb=10e-9, tr=1e-9, tj=0)
	>>> Vi.plotV('PRBS Test')
	"""
	
	def __init__(self, bits=8, v1=0, v2=1, tb=10e-9, tr=1e-9, tj=10e-12, 
			resolution = 1e3):
		"""
		Arguments:
		periods -- number of bits
		v1 -- voltage level in in state "0" (volt)
		v2 -- voltage level in in state "1" (volt)
		tb -- width of single bit (seconds)
		tr -- rise/fall times -- 20%-80% -- (seconds)
		tj -- jitter -- standard deviation -- (seconds)
		resolution -- time points per bit
		"""

		states = numpy.zeros(bits)
		for i in range(0,bits):
			states[i] = random.randint(0,1)
		
		Gauss.__init__(self, states, v1, v2, tb, tr, tj, resolution)

if __name__ == '__main__':
	
	import doctest
	doctest.testmod(verbose=False)
	print('Testing Complete')
	plot.show()	
