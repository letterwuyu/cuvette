from common.test_base import TestBase
from .ior_wapper import IORWapper
from common.config import DefaultConfig
from common.report import RetPrint

class IORPerformance(TestBase):

    header = ['task', 'all_write_max',
              'all_write_min',
              'all_write_mean',
              'all_read_max',
              'all_read_min',
              'all_read_mean']

    def __init__(self):
        super(IORPerformance, self).__init__()
        self._options = None
        self._report = RetPrint().get_report()
        self._report.add_header('ior', self.header)

    def initialize(self, options):
        self._options = options

    def run(self):
        for option in self._options:
            json_summary = self._run_wapper(option['ior_option'],
                                            option['mpi_option'])
            json_summary['task'] = option['name']
            self._run_report(json_summary)

    def _run_wapper(self, ior_option, mpi_option):
        wapper = IORWapper(ior_option, mpi_option)
        wapper.run()
        json_summary = wapper.get_json_summary()
        return json_summary

    def _run_report(self, data):
        row = []
        for i in self.header:
            row.append(data[i])
        self._report.add_row('ior', row)
