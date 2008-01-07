import re

def memtotal_info():
  meminfo = open('/proc/meminfo', 'r')
  line = meminfo.read()
  memtotal = re.compile('(MemTotal:\s*)(\d*)( kB\n)')
  mem_re = memtotal.match(line)
  mem_amount = mem_re.group(2)
  return int(mem_amount)
