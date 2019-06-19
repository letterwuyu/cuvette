import sys
sys.path.append('../../common')
from common.wapper import Wapper
from common.cmd_runner import CmdRunner

class CosbenchWapper(Wapper):

    def __init__(self, cosbench_option):
        super(CosbenchWapper, self).__init__()
        self._cosbench_option = cosbench_option
        self._cmd_runner = CmdRunner('')
        self._json_summary = dict()
        self._txt_summary = dict()

    def get_json_summary(self):
        return self._json_summary

    def get_txt_summary(self):
        return self._txt_summary

    def run(self):
        retcode, stdout = self._cmd_runner.run(['cli.sh', 'submit', self._cosbench_option])
        while True:
            retcode, stdout = self._cmd_runner.run(['cli.sh', 'info'])
            finish = True
            for line in bytes.decode(stdout).splitlines():
                if 'active' in line:
                    finish = False
                    break
            if finish:
                break
        self._parse_output(bytes.decode(stdout).splitlines())
