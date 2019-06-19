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

DOCUMENTATION = '''
---
module: rbd
description:
  - A module used to create rbd.
'''
EXAMPLES = '''
- name: create rbd
  rbd:
    rbd_name: volume1
    pool_name: rbd
    size: 1G
    state: absent
'''


class Rbd(object):
    def __init__(self, rbd_name, pool_name, container_name=''):
        self.rbd_name = rbd_name
        self.pool_name = pool_name
        self.full_name = '{0}/{1}'.format(pool_name, rbd_name)
        self.changed = False
        self.message = None
        if container_name == '':
            self.container_name = None
        else:
            self.container_name = container_name

    def _run(self, cmd):
        _prefix = []
        if self.container_name:
            _prefix = ['docker', 'exec', self.container_name]
        cmd = _prefix + cmd
        proc = subprocess.Popen(cmd,  # nosec
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        retcode = proc.poll()
        if retcode != 0:
            output = 'stdout: "%s", stderr: "%s"' % (stdout, stderr)
            raise subprocess.CalledProcessError(retcode, cmd, output)
        return retcode, stdout

    def _have_create(self):
        cmd = ['rbd', 'info', self.full_name]
        try:
            status, output = self._run(cmd)
        except subprocess.CalledProcessError:
            return False
        return True

    def create(self, size, feature):
        if(self._have_create()):
            cmd = ['rbd', 'resize', self.full_name, '--size', size]
        else:
            cmd = ['rbd', 'create', self.full_name, '--size', size]
        self._run(cmd)
        cmd = ['rbd', 'info', self.full_name, '--format=json']
        retcode, stdout = self._run(cmd)
        old_feature_list = json.loads(stdout)['features']
        if old_feature_list != feature.split(','):
            old_feature_list.remove('layering')
            if len(old_feature_list):
                cmd = ['rbd', 'feature', 'disable', self.full_name, ','.join(old_feature_list)]
                self._run(cmd)
            feature_list = feature.split(',').remove('layering')
            if feature_list and len(feature_list):
                cmd = ['rbd', 'feature', 'enable', self.full_name, ','.join(feature_list)]
                self._run(cmd)

    def destroy(self):
        if(self._have_create()):
            cmd = ['rbd', 'delete', self.full_name]
            self._run(cmd)

def main():
    specs = dict(
        rbd_name=dict(type='str', required=True),
        pool_name=dict(type='str', required=True),
        state=dict(type='str', required=True),
        size=dict(type='str', required=True),
        feature=dict(type='str', default=''),
        container_name=dict(type='str', default='')
    )
    module = AnsibleModule(argument_spec=specs)  # noqa
    params = module.params
    rbd = Rbd(params['rbd_name'],
              params['pool_name'])
    try:
        if params['state'] == 'present':
            rbd.create(params['size'],
                       params['feature'])
        elif params['state'] == 'absent':
            rbd.destroy()
        module.exit_json(changed=rbd.changed,
                         message=rbd.message)
    except subprocess.CalledProcessError as ex:
        msg = ('Failed to call command: %s returncode: %s output: %s' %
               (ex.cmd, ex.returncode, ex.output))
        module.fail_json(msg=msg)


from ansible.module_utils.basic import *  # noqa
if __name__ == "__main__":
    main()
