import atexit
from .tools import write_string
from .singleton import SingletonType
from .config import DefaultConfig
from abc import ABCMeta, abstractmethod
from prettytable import PrettyTable

class ReportMain(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        super(ReportMain, self).__init__()

    @abstractmethod
    def add_header(self, name):
        pass

    @abstractmethod
    def add_row(self, name, row):
        pass

class CSVMain(ReportMain):

    def __init__(self):
        super(CSVMain, self).__init__()
        self._filename = DefaultConfig().get('collect')
        self._units = {}
        atexit.register(self.cleanup)

    def cleanup(self):
        str_buf = ''
        for k, v in self._units.items():
            str_buf += v.get_view()
            str_buf += '\n'
        write_string(self._filename, str_buf)

    def add_header(self, name, header):
        if name in self._units:
            return False
        self._units[name] = CSVMain.CSVUnit(header)
        return True

    def add_row(self, name, row):
        self._units[name].add_row(row)

    class CSVUnit:
        def __init__(self, header):
            self._data = [header]

        def add_row(self, row):
            self._data.append(row)

        def get_view(self):
            str_buf = ''
            for row in self._data:
                str_buf += ','.join(row) + '\n'
            return str_buf


class PrettyMain(ReportMain):

    def __init__(self):
        super(PrettyMain, self).__init__()
        self._prettys = {}
        atexit.register(self.cleanup)

    def cleanup(self):
        for k, v in self._prettys.items():
            print("\n--------{}----------".format(k))
            print (v.get_view())

    def add_header(self, name, header):
        self._prettys[name] = PrettyMain.PrettyUnit(header)

    def add_row(self, name, row):
        self._prettys[name].add_row(row)

    class PrettyUnit:
        def __init__(self, header):
            self._pt = PrettyTable(header)

        def add_row(self, row):
            self._pt.add_row(row)

        def get_view(self):
            return self._pt

class RetPrint(object):

    __metaclass__ = SingletonType

    def __init__(self, report_type):
        self._report = self._create_report(report_type)

    def _create_report(self, report_type):
        if report_type == 'terminal':
            return PrettyMain()
        elif report_type == 'csv':
            return CSVMain()

    def get_report(self):
        return self._report
