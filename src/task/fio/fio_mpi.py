import sys
sys.path.append('/root/code/cuvette/src')
from common.mpi_runner import MpiRunner

if __name__ == '__main__':
    is_main, collect_stdout = MpiRunner().run(['fio'] + sys.argv[1].split())
    if is_main:
        print(collect_stdout)
