from common.test_base import TestBase
from .mdtest_wapper import MDTestWapper
from common.config import DefaultConfig
from common.report import RetPrint

class MDTestPerformance(TestBase):

    header = ['task', 'dir_creation', 'dir_stat',
              'dir_removal', 'file_creation',
              'file_stat', 'file_remove',
              'tree_create', 'tree_remove']

    def __init__(self):
        super(MDTestPerformance, self).__init__()
        self._options = None
        self._report = RetPrint().get_report()
        self._report.add_header('mdtest', self.header)

    def initialize(self, options):
        self._options = options

    def run(self):
        for option in self._options:
            json_summary = self._run_wapper(option['mdtest_option'],
                                            option['mpi_option'])
            json_summary['task'] = option['name']
            self._run_report(json_summary)

    def _run_wapper(self, mdtest_option, mpi_option):
        wapper = MDTestWapper(mdtest_option, mpi_option)
        wapper.run()
        json_summary = wapper.get_json_summary()
        return json_summary

    def _run_report(self, data):
        row = []
        for i in self.header:
            row.append(data[i])
        self._report.add_row('mdtest', row)
