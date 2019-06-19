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
  - A module used to create fio confurge file.
'''
EXAMPLES = '''
- name: create fioconf
  fioconf:
    filepath: /etc/txt1
    bs: 4k
    state: absent
'''


class Fioconf(object):
    def __init__(self, filepath):
        self.conf = {}
        self.filepath = filepath
        self.changed = False
        self.message = ""

    def file_exists(self):
        return os.path.exists(self.filepath)

    def new_create(self):
        self.destroy()
        os.mknod(self.filepath, 0766)

    def create(self, bs, rw, iodepth, ioengine, direct, filename,
               runtime, numjobs):
        self.conf['bs'] = bs
        self.conf['rw'] = rw
        self.conf['iodepth'] = iodepth
        self.conf['ioengine'] = ioengine
        self.conf['direct'] = direct
        self.conf['runtime'] = runtime
        self.conf['numjobs'] = numjobs
        if ioengine != 'rbd':
            self.conf['filename'] = filename
        else:
            path_list = filename.split('/')
            self.conf['clientname'] = path_list[0]
            self.conf['pool'] = path_list[1]
            self.conf['rbdname'] = path_list[2]

        self.new_create()

        fo = open(self.filepath, "w")
        fo.writelines("[fio]\n")
        for k, v in self.conf.items():
            fo.writelines("{0}={1}\n".format(k, v))
        fo.close()


    def destroy(self):
        if(self.file_exists()):
            os.remove(self.filepath)

def main():
    specs = dict(
        filepath=dict(type='str', required=True),
        bs=dict(type='str', default='4k'),
        rw=dict(type='str', default='randwrite'),
        iodepth=dict(type='str', default='32'),
        ioengine=dict(type='str', default='libaio'),
        direct=dict(type='str', default='1'),
        filename=dict(type='str', default=''),
        runtime=dict(type='str', default='300'),
        numjobs=dict(type='str', default='1'),
        state=dict(type='str', default='present')
    )
    module = AnsibleModule(argument_spec=specs)  # noqa
    params = module.params
    fioconf = Fioconf(params['filepath'])
    try:
        if params['state'] == 'present':
            fioconf.create(params['bs'], params['rw'], params['iodepth'],
                       params['ioengine'], params['direct'],
                       params['filename'], params['runtime'],
                       params['numjobs'])
        elif params['state'] == 'absent':
            fioconf.destroy()
        module.exit_json(changed=fioconf.changed,
                         message=fioconf.message)
    except subprocess.CalledProcessError as ex:
        msg = ('Failed to call command: %s returncode: %s output: %s' %
               (ex.cmd, ex.returncode, ex.output))
        module.fail_json(msg=msg)


from ansible.module_utils.basic import *  # noqa
if __name__ == "__main__":
    main()
