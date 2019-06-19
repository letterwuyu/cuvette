#!/usr/bin/env python

# Copyright 2019 unitedstack
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import subprocess  # nosec
import os

DOCUMENTATION = '''
---
module: iorconf
description:
  - A module used to create ior confurge file.
'''
EXAMPLES = '''
- name: create iorconf
  iorconf:
    filename: /etc/txt1
    testFile: /mnt/testdir
    state: absent
'''


class Iorconf(object):
    def __init__(self, filepath):
        self.conf = {}
        self.filepath = filepath
        self.changed=False
        self.message=""

    def file_exists(self):
        return os.path.exists(self.filepath)

    def new_create(self):
        self.destroy()
        os.mknod(self.filepath, 0766)

    def create(self, api, hintsFile, testFile, repetitions, readFile,
               writeFile, filePerProc, segmentCount, blockSize,
               transferSize, collective, testdirs, npernode):
        if hintsFile == '':
           hintsFile = 'hintsFile'
        dirs = []
        testdirs = testdirs.split(',')
        for dirpath in testdirs:
            for num in range(0, int(npernode)):
                dirs.append('{0}/dir{1}'.format(dirpath, num)) 

        self.conf['api'] = api
        self.conf['hintsFileName'] = hintsFile
        self.conf['testFile'] = '@'.join(dirs)
        self.conf['repetitions'] = repetitions
        self.conf['readFile'] = readFile
        self.conf['writeFile'] = writeFile
        self.conf['filePerProc'] = filePerProc
        self.conf['segmentCount'] = segmentCount
        self.conf['blockSize'] = blockSize
        self.conf['transferSize'] = transferSize
        self.conf['collective'] = collective

#        self.new_create()

        fo = open(self.filepath, "w")
        fo.writelines("===============> start script <===============\nIOR START\n")
        for k, v in self.conf.items():
            fo.writelines("    {0}={1}\n".format(k, v))
        fo.writelines("IOR STOP\n===============> stop script <===============\n")
        fo.close()


    def destroy(self):
        if(self.file_exists()):
            os.remove(self.filepath)

def main():
    specs = dict(
        filepath = dict(type='str', required=True),
        api=dict(type='str', default='POSIX'),
        hintsFile=dict(type='str', default='hintsFile'),
        testFile=dict(type='str', required=''),
        repetitions=dict(type='str', default='1'),
        readFile=dict(type='str', default='1'),
        writeFile=dict(type='str', default='1'),
        filePerProc=dict(type='str', default='1'),
        segmentCount=dict(type='str', default='1'),
        blockSize=dict(type='str', default='32g'),
        transferSize=dict(type='str', default='1024k'),
        collective=dict(type='str', default='0'),
        testdirs=dict(type='str', default=''),
        npernode=dict(type='int', default=1),
        state=dict(type='str', default="present")
    )
    module = AnsibleModule(argument_spec=specs)  # noqa
    params = module.params
    iorconf = Iorconf(params['filepath'])
    try:
        if params['state'] == 'present':
            iorconf.create(params['api'], params['hintsFile'],
                       params['testFile'], params['repetitions'],
                       params['readFile'], params['writeFile'],
                       params['filePerProc'], params['segmentCount'],
                       params['blockSize'], params['transferSize'],
                       params['collective'], params['testdirs'],
                       params['npernode'])
        elif params['state'] == 'absent':
            iorconf.destroy()
        module.exit_json(changed=iorconf.changed,
                         message=iorconf.message)
    except subprocess.CalledProcessError as ex:
        msg = ('Failed to call command: %s returncode: %s output: %s' %
               (ex.cmd, ex.returncode, ex.output))
        module.fail_json(msg=msg)


from ansible.module_utils.basic import *  # noqa
if __name__ == "__main__":
    main()
