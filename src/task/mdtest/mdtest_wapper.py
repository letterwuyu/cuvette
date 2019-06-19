import sys
sys.path.append('../../common')
from common.wapper import Wapper
from common.cmd_runner import CmdRunner

class MDTestWapper(Wapper):

    def __init__(self, mdtest_option, mpi_option):
        super(MDTestWapper, self).__init__()
        self._mdtest_option = mdtest_option.split()
        self._mpi_option = mpi_option.split()
        self._cmd = self._mpi_option + ['mdtest'] + self._mdtest_option
        self._cmd_runner = CmdRunner('mpirun --allow-run-as-root')
        self._json_summary = dict()
        self._txt_summary = dict()

    def get_json_summary(self):
        return self._json_summary

    def get_txt_summary(self):
        return self._txt_summary

    def run(self):
        retcode, stdout = self._cmd_runner.run(self._cmd)
        self._txt_summary = stdout
        self._parse_output(bytes.decode(stdout).splitlines())

    def _build_avg_summary(self, line_toks):
        summary = dict()
#        summary['max'] = line_toks[1]
#        summary['min'] = line_toks[2]
#        summary['mean'] = line_toks[3]
#        summary['stddev'] = line_toks[4]
        summary = line_toks[3]
        return summary

    def _parse_output(self, lines):
        for line in lines:
            if line.startswith('mdtest'):
                line_toks = line.split(' ')
                self._json_summary['mdtest_version'] = line_toks[0]
                first = True
                for tok in line_toks:
                    if (tok.isdigit() and first):
                        self._json_summary['num_tasks'] = tok
                        first = False
                    elif (tok.isdigit()):
                        self._json_summary['num_nodes'] = tok
            elif (line.startswith('   Directory creation:')):
                self._json_summary['dir_creation'] = self._build_avg_summary(line.split()[1:])
            elif (line.startswith('   Directory stat')):
                self._json_summary['dir_stat'] = self._build_avg_summary(line.split()[2:])
            elif (line.startswith('   Directory removal')):
                self._json_summary['dir_removal'] = self._build_avg_summary(line.split()[2:])
            elif (line.startswith('   File creation')):
                self._json_summary['file_creation'] = self._build_avg_summary(line.split()[2:])
            elif (line.startswith('   File stat')):
                self._json_summary['file_stat'] = self._build_avg_summary(line.split()[2:])
            elif (line.startswith('   File removal')):
                self._json_summary['file_remove'] = self._build_avg_summary(line.split()[2:])
            elif (line.startswith('   Tree creation')):
                self._json_summary['tree_create'] = self._build_avg_summary(line.split()[2:])
            elif (line.startswith('   Tree removal')):
                self._json_summary['tree_remove'] = self._build_avg_summary(line.split()[2:])
