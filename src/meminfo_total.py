#  Copyright Andrew Hunter, 2008
#
#    This program is free software; you may redistribute it and/or modify it
#    under the terms of the GNU General Public License as published by the Free 
#    Software Foundation; either version 2 of the License, or (at your option) 
#    any later version.
#
#    This program is distributed in the hope that it will be useful, but WITHOUT
#    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or 
#    FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for 
#    more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re

def meminfo_total():
  meminfo = open('/proc/meminfo', 'r')
  line = meminfo.read()
  memtotal = re.compile('(MemTotal:\s*)(\d*)( kB\n)')
  mem_re = memtotal.match(line)
  mem_amount = mem_re.group(2)
  return int(mem_amount)
