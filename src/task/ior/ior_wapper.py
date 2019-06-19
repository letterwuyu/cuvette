import sys
sys.path.append('../../common')
from common.wapper import Wapper
from common.cmd_runner import CmdRunner
import re

class IORWapper(Wapper):

    def __init__(self, ior_option, mpi_option):
        super(IORWapper, self).__init__()
        self._ior_option = ior_option.split()
        self._mpi_option = mpi_option.split()
        self._cmd = self._mpi_option + ['ior'] + self._ior_option
        self._cmd_runner = CmdRunner('mpirun --allow-run-as-root')
        self._json_summary = dict()
        self._txt_summary = dict()
        self._units = None
        self._all_units = None

    def get_json_summary(self):
        return self._json_summary

    def get_txt_summary(self):
        return self._txt_summary

    def run(self):
        retcode, stdout = self._cmd_runner.run(self._cmd)
        self._txt_summary = stdout
        self._parse_output(bytes.decode(stdout).splitlines())

    def _build_avg_summary(self, rw, line_toks):
        self._json_summary[rw + '_' + 'bw']    = line_toks[0] + self._units[0]
        self._json_summary[rw + '_' + 'block'] = line_toks[1] + self._units[1]
        self._json_summary[rw + '_' + 'xfer']  = line_toks[2] + self._units[2]
        self._json_summary[rw + '_' + 'open']  = line_toks[3] + self._units[3]
        self._json_summary[rw + '_' + 'wr/rd'] = line_toks[4] + self._units[4]
        self._json_summary[rw + '_' + 'close'] = line_toks[5] + self._units[5]
        self._json_summary[rw + '_' + 'tatal'] = line_toks[6] + self._units[6]
        self._json_summary[rw + '_' + 'iter']  = line_toks[7]

    def _build_all_summary(self, rw, line_toks):
        self._json_summary[rw + '_' + 'max'] = line_toks[0] + self._all_units[0]
        self._json_summary[rw + '_' + 'min'] = line_toks[1] + self._all_units[1]
        self._json_summary[rw + '_' + 'mean'] = line_toks[2] + self._all_units[2]
        self._json_summary[rw + '_' + 'stddev'] = line_toks[3]
        self._json_summary[rw + '_' + 'means'] = line_toks[4]

    def _parse_output(self, lines):
        have_summary_avg = False
        for line in lines:
            if line.startswith('IOR'):
                line_toks = line.split(':')
                self._json_summary['ior_version'] = line_toks[0]
            elif line.startswith('Command line used'):
                line_toks = line.split(' ')
                self._json_summary['command'] = line_toks[3]
            elif line.startswith('  clients'):
                line_toks = line.split()
                self._json_summary['num_nodes'] = line_toks[2]
                toks = line_toks[3].split(' ')
                self._json_summary['num_tasks'] = toks[1:]
            elif line.startswith('access'):
                self._units = re.findall(r'[(](.*?)[)]', line)
            elif line.startswith('Operation'):
                self._all_units = re.findall(r'[(](.*?)[)]', line)
            elif line.startswith('write'):
                if have_summary_avg:
                    self._build_all_summary('all_write', line.split()[1:])
                else:   
                    self._build_avg_summary('write', line.split()[1:])
            elif line.startswith('read'):
                if have_summary_avg:
                    self._build_all_summary('all_read', line.split()[1:])
                else:
                    self._build_avg_summary('read', line.split()[1:])
            elif line.startswith('remove') and not have_summary_avg:
                self._json_summary['remove'] = self._build_avg_summary('remove', line.split()[1:])
            elif line.startswith('Max Write'):
                self._json_summary['max_write'] = line.split()[1]
                have_summary_avg = True
            elif line.startswith('Max Read'):
                self._json_summary['max_read'] = line.split()[1]
