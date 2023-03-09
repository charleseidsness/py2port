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
The functions in this module can be used to calculate the nearest standard
value capacitor and resistor values.

Functions:
resistor - returns the closest standard resistor value
capacitor - returns the closest standard capacitor value

"""

from . import units
import math

def res(value, tol=1):
	"""
	Returns the closest standard resistor value.
	
	Arguments:
	value -- resistance value, float or string with units
	tol -- tolerance, 1, 2, 5, 10 (in percentage) -- deafault 1
	
	Example:
	>>> R = res('89.8')
	>>> print "%0.1f" % R
	90.9
	"""
		
	if tol == 1:
		N = 96
		figs = 1
	elif tol == 2:
		N = 48
		figs = 1
	elif tol == 5:
		N = 24
		figs = 0
	elif tol == 10:
		N = 12
		figs = 0
	else:
		raise RuntimeError('Tolearnce must be 1%, 2%, 5%, or 10%')
		
	value = units.float(value)
	dec = (math.floor(math.log10(value))-1)
	
	value = value/10**dec
	i = round(math.log10(value)*N)
	
	return 10**dec*round(10**(i/N),figs)

def cap(value, tol=5):
	"""
	Returns the closest standard capacitor value.
	
	Arguments:
	value -- resistance value, float or string with units
	tol -- tolerance, 1, 2, 5, 10 (in percentage) -- deafault 5
	
	Example:
	>>> C = cap('12.72')
	>>> print "%0.1f" % C
	13.0
	"""
	
	return res(value, tol)

# --------------------------------------------------------------------------- #

if __name__ == '__main__':
	
	import doctest
	doctest.testmod(verbose=False)
	print('Testing Complete')
	