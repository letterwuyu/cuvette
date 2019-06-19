from .fio_wapper import FIOWapper
from common.test_base import TestBase
from common.config import DefaultConfig
from common.report import RetPrint

class FIOPerformance(TestBase):

    header = ['task', 'bs', 'iodepth', 'num_jobs', 'iops_avg',
              'bw_avg', 'lat_avg', 'lat_min', 'lat_max',
              'stdev', '99']

    def __init__(self):
        super(FIOPerformance, self).__init__()
        self._options = None
        self._report = RetPrint().get_report()
        self._report.add_header('fio', self.header)

    def initialize(self, options):
        self._options = options

    def run(self):
        for option in self._options:
            json_summary = self._run_wapper(option['fio_option'],
                                            option['mpi_option'])
            json_summary['task'] = option['name']
            self._run_report(json_summary)

    def _run_wapper(self, fio_option, mpi_option):
        wapper = FIOWapper(fio_option, mpi_option)
        wapper.run()
        json_summary = wapper.get_json_summary()
        return json_summary

    def _run_report(self, data):
        row = []
        for i in self.header:
            row.append(data[i])
        self._report.add_row('fio', row)
