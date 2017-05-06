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
This module contains classes and fuunctions used to plot circuit responses.

Classes:

Functions:

Examples:

"""

import pylab
import numpy
import units

def live():
	"""
	If running from the Python Shell, will put matplotlib (pylab)
	into interactive mode so you can plot as you go.
	"""
	pylab.ion()

def dB(value):
	return 20*numpy.log10(abs(value))

def phase(value):
	return numpy.angle(value, deg=True)

ONEPORT_Z = 0		# One-Port Impedance Plots
TWOPORT_ZIN_OC = 1	# Two-Port Open-Circuit Input Impedance Plots
TWOPORT_ZOUT_OC = 2	# Two-Port Open-Circuit Output Impedance Plots
TWOPORT_GF_OC = 3	# Two-Port Open-Circuit Forward Gain Plots
TWOPORT_GR_OC = 4	# Two-Port Open-Circuit Reverse Gain Plots
WAVEFORM_V_T = 5	# Waveform Voltage Plots in Time Domain
WAVEFORM_I_T = 6	# Waveform Current Plots in Time Domain
WAVEFORM_V_F = 7	# Waveform Voltage Plots in fcuency Domain
WAVEFORM_I_F = 8	# Waveform Current Plots in fcuency Domain

class Plot:
	"""
	Plots are added to this class and then displayed all at once with
	a call to the show method.
	"""
	
	def __init__(self):
		self.colours = ['b', 'r', 'g', 'c', 'm', 'y']
		
		self.plotName = ['One Port Impedance',
				'Two Port Input Impedance (Open-Circuit)', 
				'Two Port Output Impedance (Open-Circuit)', 
				'Two Port Forward Gain (Open-Circuit)', 
				'Two Port Reverse Gain (Open-Circuit)',
				'Voltage', 
				'Current',
				'Voltage', 
				'Current']
		self.yLabel = ['|Z| (Ohms)',
				'|Z| (Ohms)', 
				'|Z| (Ohms)', 
				('Gain (dB)', 'Phase (deg)'), 
				('Gain (dB)', 'Phase (deg)'),
				'Voltage (V)',
				'Current (A)',
				'Voltage (V)',
				'Current (A)']
		self.xLabel = ['Frequency (Hz)',
				'Frequency (Hz)', 
				'Frequency (Hz)', 
				'Frequency (Hz)', 
				'Frequency (Hz)', 
				'Time (s)', 
				'Time (s)',
				'Frequency (Hz)',
				'Frequency (Hz)']
				
		N = len(self.plotName)
		self.plotColour = pylab.zeros((N,),dtype=int)
		self.plotExists = pylab.zeros((N,))
		
	
	def _addPlot(self, fc, data, fig, plotter, label, symbol=''):
		self.plotExists[fig] = 1
		pylab.figure(fig)
		plotter(fc, data, symbol + 
				self.colours[self.plotColour[fig]],
				label=label
		)
		self.plotColour[fig] += 1
		self.plotColour[fig] = self.plotColour[fig]%(len(self.colours))

	def _addDblPlot(self, fc, data, phase, fig, plotter, label, symbol=''):
		self.plotExists[fig] = 1
		pylab.figure(fig)
		pylab.subplot(211)
		plotter(fc, data, symbol + 
				self.colours[self.plotColour[fig]],
				label=label
		)
		pylab.subplot(212)
		plotter(fc, phase, symbol + 
				self.colours[self.plotColour[fig]],
				label=label
		)
		pylab.subplot(211)
		self.plotColour[fig] += 1
		self.plotColour[fig] = self.plotColour[fig]%(len(self.colours))
	
	def addZPlot(self, fc, z, label='none'):
		"""
		Add a new impedance plot.
		
		Arguments:
		fc -- list of fcuencies to plot at
		z -- list of impedances to plot
		name -- name of this partucular plot -- default = 'none'
		"""
		self._addPlot(fc, abs(z), ONEPORT_Z, pylab.loglog, label)		
	
	def addZinPlot(self, fc, z, label='none'):
		"""
		Add a new input impedance plot, see addZPlot.		
		"""
		self._addPlot(fc, abs(z), TWOPORT_ZIN_OC, pylab.loglog, label)
	
	def addZoutPlot(self, fc, z, label='none'):
		"""
		Add a new output impedance plot, see addZPlot.		
		"""
		self._addPlot(fc, abs(z), TWOPORT_ZOUT_OC, pylab.loglog, label)
	
	def addGfPlot(self, fc, g, label='none'):
		"""
		Add a new forward gain plot, see addZPlot.		
		"""
		self._addDblPlot(fc, dB(g), phase(g), TWOPORT_GF_OC, pylab.semilogx, label)
	
	def addGrPlot(self, fc, g, label='none'):
		"""
		Add a new reverse gain plot, see addZPlot.		
		"""
		self._addDblPlot(fc, dB(g), phase(g), TWOPORT_GR_OC, pylab.semilogx, label)
	
	def addVTPlot(self, time, v, label='none', symbol = ''):
		"""
		Add a new voltage plot in the time domain, see addZPlot.
		"""
		self._addPlot(time, v, WAVEFORM_V_T, pylab.plot, label, symbol)
	
	def addITPlot(self, time, i, label='none'):
		"""
		Add a new current plot in the time domain, see addZPlot.
		"""
		self._addPlot(time, i, WAVEFORM_I_T, pylab.plot, label)
	
	def addVFPlot(self, fc, v, label='none'):
		"""
		Add a new voltage plot in the frequency domain, see addZPlot.
		"""
		self._addPlot(fc, abs(v), WAVEFORM_V_F, pylab.loglog, label)
	
	def addIFPlot(self, fc, i, label='none'):
		"""
		Add a new current plot in the frequency domain, see addZPlot.
		"""
		self._addPlot(fc, abs(i), WAVEFORM_I_F, pylab.loglog, label)

	def show(self):
		"""
		Display all of the generated plots.		
		"""
		
		plot = False
		for i in range(0, len(self.plotName)):
			if self.plotExists[i] == 1:
				pylab.figure(i)
				pylab.title(self.plotName[i])
				pylab.legend()
				if type(self.yLabel[i]) == tuple:
					pylab.subplot(211)
					pylab.ylabel(self.yLabel[i][0])
					pylab.xlabel(self.xLabel[i])
					pylab.subplot(212)
					pylab.ylabel(self.yLabel[i][1])
					pylab.xlabel(self.xLabel[i])
				else:
					pylab.ylabel(self.yLabel[i])
					pylab.xlabel(self.xLabel[i])
				plot = True
	
		if (plot == True):	
			pylab.show()
		
		

plot = Plot()
# --------------------------------------------------------------------------- #

if __name__ == '__main__':
	
	import doctest
	doctest.testmod(verbose=False)
	print 'Testing Complete'
	plot.show()

	
