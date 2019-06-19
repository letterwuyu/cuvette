from task.mdtest.mdtest_performance import MDTestPerformance
from task.ior.ior_performance import IORPerformance
from task.fio.fio_performance import FIOPerformance

class Factory(object):

    def __init__(self):
        pass

    def create(self, module):
        module = module.upper()
        if module == 'MDTEST':
            return MDTestPerformance()
        elif module == 'IOR':
            return IORPerformance()
        elif module == 'FIO':
            return FIOPerformance()

