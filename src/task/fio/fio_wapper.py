from common.wapper import Wapper
from common.cmd_runner import CmdRunner
from common.unit_convert import ByteConversion, SecConversion
from common.config import DefaultConfig
import re

class FIOWapper(Wapper):

    def __init__(self, fio_option, mpi_option):
        super(FIOWapper, self).__init__()
        self._fio_mpi_option = fio_option.split()
        self._mpi_option = mpi_option.split()
        self._cmd = self._mpi_option + ['python3', '/root/code/cuvette/src/task/fio/fio_mpi.py'] + self._fio_mpi_option
        self._cmd_runner = CmdRunner('mpirun --allow-run-as-root')
        self._json_summary = None
        self._txt_summary = None
        self._bw_convert = ByteConversion(['Bytes', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB'])
        self._iops_convert = ByteConversion(['null', 'K', 'M', 'G', 'T', 'P'])
        self._sec_convert = SecConversion()

        config = DefaultConfig()
        self._fio_iops_unit = config.get('fio_iops_unit')
        self._fio_bw_unit = config.get('fio_bw_unit')
        self._fio_lat_unit = config.get('fio_lat_unit')

    def get_json_summary(self):
        return self._json_summary

    def get_txt_summary(self):
        return self._txt_summary

    def run(self):
        retcode, stdout = self._cmd_runner.run(self._cmd)
        self._txt_summary = stdout
        self._parse_output(bytes.decode(stdout).splitlines())

    def _initialize_summary(self):
        self._json_summary = dict()
        self._json_summary['iops_avg'] = '0'
        self._json_summary['bw_avg'] = '0'

    def _add_iops(self, iops):
         iops = self._iops_convert.format(iops, self._fio_iops_unit)
         iops_num = self._iops_convert.num(iops)
         src_iops_num = self._iops_convert.num(self._json_summary['iops_avg'])
         self._json_summary['iops_avg'] = ('%.2f' + ' ' + self._fio_iops_unit) % (src_iops_num + iops_num)

    def _add_bw(self, bw):
        bw = self._bw_convert.format(bw, self._fio_bw_unit)
        bw_num = self._bw_convert.num(bw)
        src_bw_num = self._bw_convert.num(self._json_summary['bw_avg'])
        self._json_summary['bw_avg'] = ('%.2f' + ' ' + self._fio_bw_unit) % (src_bw_num + bw_num)

    def _add_lat(self, item, lat):
        lat = self._sec_convert.format(lat, self._fio_lat_unit)
        lat_num = self._sec_convert.num(lat)
        if item not in self._json_summary:
            self._json_summary[item] = ('%.2f' + ' ' + self._fio_lat_unit) % lat_num
            return
        src_lat_num = self._sec_convert.num(self._json_summary[item])
        if item == 'lat_avg':
            self._json_summary[item] = ('%.2f' + ' ' + self._fio_lat_unit) % ((src_lat_num + lat_num) / 2.0)
        elif item == 'lat_max':
            self._json_summary[item] = ('%.2f' + ' ' + self._fio_lat_unit) % \
                (src_lat_num if (src_lat_num > lat_num) else lat_num)
        elif item == 'lat_min':
            self._json_summary[item] = ('%.2f' + ' ' + self._fio_lat_unit) % \
                (src_lat_num if (src_lat_num < lat_num) else lat_num)
        elif item == 'stdev':
            self._json_summary[item] = ('%.2f' + ' ' + self._fio_lat_unit) % ((src_lat_num + lat_num) / 2.0)
        elif item == '99':
            self._json_summary[item] = ('%.2f' + ' ' + self._fio_lat_unit) %  \
                (src_lat_num if (src_lat_num > lat_num) else lat_num) 

    def _parse_output(self, lines):
        self._initialize_summary()
        clat_unit = ''
        for line in lines:
            if 'bs=(R)' in line:
                for line_toks in line.split(':'):
                    if 'rw=' in line_toks:
                        toks = line_toks.replace(' ', '').split(',')
                        self._json_summary['bs'] = toks[1].split('=')[1].split('-')[1]
                        self._json_summary['iodepth'] = toks[-1].split('=')[1]
            elif line.startswith('     lat'):
                unit = ''
                for line_toks in line.split(':'):
                    if line_toks.startswith('     lat ('):
                        unit = re.findall(r'[(](.*?)[)]', line_toks.split()[1])[0]
                    elif line_toks.startswith(' min'):
                        toks = line_toks.split(',')
                        self._add_lat('lat_min', toks[0].split('=')[1] + unit)
                        self._add_lat('lat_max', toks[1].split('=')[1] + unit)
                        self._add_lat('lat_avg', toks[2].split('=')[1] + unit)
                        self._add_lat('stdev',   toks[3].split('=')[1] + unit)
            elif line.startswith('    clat percentiles'):
                clat_unit = re.findall(r'[(](.*?)[)]', line)[0]
            elif '99.00th' in line:
                for line_toks in line.split(','):
                    if '99.00th' in line_toks:
                        num = re.findall(r'[(](.*?)[)]', line_toks.replace('[', '(').replace(']', ')'))[0]
                        self._add_lat('99', num + clat_unit)
                        break
            elif line.startswith('   bw'):
                unit = ''
                for line_toks in line.split(':'):
                    if line_toks.startswith('   bw'):
                        unit =  re.findall(r'[(](.*?)[)]', line_toks)[0].split('/')[0].replace(' ', '')
                    elif line_toks.startswith(' min'):
                        self._add_bw(line_toks.split(',')[3].split('=')[1] + unit)
            elif line.startswith('   iops'):
                unit = ''
                for line_toks in line.split(':'):
                    if line_toks.startswith(' min'):
                        self._add_iops(line_toks.split(',')[2].split('=')[1] + unit)
            elif line.startswith('Starting'):
                self._json_summary['num_jobs'] = line.split(' ')[1]

