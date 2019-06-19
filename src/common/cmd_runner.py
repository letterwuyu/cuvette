import subprocess

class CmdRunner(object):
    def __init__(self, cmd_prefix=''):
        self._cmd_prefix = cmd_prefix

    def run(self, cmd):
        cmd = self._cmd_prefix.split() + cmd
        proc = subprocess.Popen(cmd,  # nosec
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        retcode = proc.poll()
        if retcode != 0:
            output = 'stdout: "%s", stderr: "%s"' % (stdout, stderr)
            print (output)
            raise subprocess.CalledProcessError(retcode, cmd, output)
        return retcode, stdout
