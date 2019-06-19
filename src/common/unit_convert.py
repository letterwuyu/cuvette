import math
import re

class ByteConversion(object):

    def __init__(self,
                 units = ['Bytes','KB','MB','GB','TB','PB']):
        super(ByteConversion, self).__init__()
        self._units = units
        self._default_cur_unit = units[0]

    def set_default_cur_unit(self, unit):
        self._default_cur_unit = unit

    def format(self, size, unit):
        if not re.search('[a-z]', size):
            num = size
            cur_unit = self._default_cur_unit
        else:
            num = re.findall(r'-?\d+\.?\d*e?-?\d*?', size)[0]
            cur_unit = re.findall('[a-zA-Z]+', size)[0]
        distance = self._units.index(unit) - self._units.index(cur_unit)
        return ('%.2f'+" "+unit) % (float(num) / math.pow(1024, distance))

    def num(self, size):
        return float(re.findall(r'-?\d+\.?\d*e?-?\d*?', size)[0])

class SecConversion(object):

    def __init__(self,
                 units = ['nsec','usec','msec','sec']):
        self._units = units
        self._default_cur_unit = units[0]

    def set_default_cur_unit(self, unit):
        self._default_cur_unit = unit

    def format(self, size, unit):
        if not re.search('[a-z]', size):
            num = int(size)
            cur_unit = self._default_cur_unit
        else:
            num = re.findall(r'-?\d+\.?\d*e?-?\d*?', size)[0]
            cur_unit = re.findall('[a-zA-Z]+', size)[0]
        distance = self._units.index(unit) - self._units.index(cur_unit)
        return ('%.2f'+" "+unit) % (float(num) / math.pow(1000, distance))
    
    def num(self, size):
        return float(re.findall(r'-?\d+\.?\d*e?-?\d*?', size)[0])
