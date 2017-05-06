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
py2port is a tool for performing two-port and one-port analysis on linear 
circuits. It was developed for analysing PCB Power-Distribution-Systems and 
lossy-transmission lines but can be used as a more general purpose simulation
tool.

For more information refer to the twoport webpage:
<www.thedigitalmachine.net/twoport.html> and use the Python help command
to print module and class docstrings.

Dependencies:
matplotlib -- <http://matplotlib.sourceforge.net/>
numpy -- <http://numpy.scipy.org/>

Please report all bugs to:
<charles@thedigitalmachine.net>

Modules:
twoport -- two-port devices
oneport -- one-port devices
waveform -- input waveforms for time-domain responses
freq -- freqency domain points
plot -- response plotting untilities

"""

from twoport import *
from oneport import *
from waveform import *
from freq import *
from plot import *
