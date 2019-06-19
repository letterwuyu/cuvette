import argparse
import os
from common.config import *
from factory import Factory
from common.report import RetPrint

class Main(object):

    def __init__(self, args):
        self._module_conf = MoudleConfig(args.conf)
        report_type = 'terminal'
        if args.output:
            os.mknod(args.output)
            DefaultConfig().set('collect', args.output)
            report_type = 'csv'
        RetPrint(report_type)

    def run(self):
        modules = self._module_conf.get_modules()
        factory = Factory()
        for module in modules:
            test_base = factory.create(module)
            test_base.initialize(self._module_conf.get_config(module))
            test_base.run()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--conf', '-c')
    parser.add_argument('--output', '-o')
    args = parser.parse_args()
    Main(args).run()
