from mpi4py import MPI
from .cmd_runner import CmdRunner

class MpiRunner(object):    

    def __init__(self):    
        self._cmd_runner = CmdRunner()  
        self._comm = MPI.COMM_WORLD
        self._size = self._comm.Get_size()
        self._rank = self._comm.Get_rank()

    def __del__(self):
        MPI.Finalize() 

    def run(self, cmd):            
        retcode, stdout = self._cmd_runner.run(cmd) 
        self._comm.Barrier()             
        collect_stdout = self._comm.gather(stdout, root=0)
        if self._rank == 0:
            return True, "".join([ bytes.decode(item) for item in collect_stdout])
        return False, ''
