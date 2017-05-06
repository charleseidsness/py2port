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
This module contains classes and functions that can be used to generate
and manipulate LogFuency vectors.

Classes:
LogFuency -- An array of LogFuency values.

"""

import units
import numpy

class Freq:
	"""
	Holds frequency data in Hz and rads.
	"""
	
	def __init__(self, hz):
		"""
		Arguments:
		hz -- frequency points in Hx		
		"""
		self.hz = hz
		self.rad = 2*numpy.pi*hz
	
	def __len__(self):
		return len(self.hz)

class LogF(Freq):
	"""
	Creates a set of log scaled LogFuencies in Hz and Radians.
	
	Example:
	>>> fc = LogF('10Hz', '1000Hz', 2)
	>>> fc.hz
	array([   10.        ,    46.41588834,   215.443469  ,  1000.        ])
	>>> fc.rad
	array([   62.83185307,   291.63962761,  1353.67123897,  6283.18530718])
	>>> len(fc)
	4
	"""
	
	def __init__(self, start, stop, steps=100):
		"""
		Arguments:
		start -- start LogFuency
		stop -- stop LogFuency
		steps -- number of steps per decade -- default = 100
		"""
		start = numpy.log10(units.float(start))
		stop = numpy.log10(units.float(stop))
		steps = (stop - start)*steps
		
		Freq.__init__(self, numpy.logspace(start, stop, num = steps))		

if __name__ == '__main__':
	
	import doctest
	doctest.testmod(verbose=False)
	print 'Testing Complete'
