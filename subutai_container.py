#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: subutai_container

short_description: subutai container module

version_added: "2.6"

description:
    - This modules manage all life cicle of subutai containers.

options:
    name:
        description:
            - Name of container.
        required: true
    state:
        description:
        - Indicates the desired container state are installed.
        default: present
        required: true
        choices: [ absent, present, latest, started, stopped ]
    version:
        description:
            - Template version.

    token:
        description:
            - Token to access private repo.

    check:
        description:
            - Check for updates without installation.


extends_documentation_fragment:
    - subutai

author:
    - Fernando Silva (@liquuid)
'''

EXAMPLES = '''

- name: run subutai import nginx
    subutai_container:
    name: 'nginx'
    state: present
    become: true

- name: run subutai destroy nginx
    subutai_container:
    name: 'nginx'
    state: absent
    become: true

- name: upgrade nginx
    subutai_container:
    name: 'nginx'
    state: latest
    become: true

'''

RETURN = '''
container:
    description: Container affected.
    type: str
message:
    description: The output message that the sample module generates.
'''

import subprocess
from ansible.module_utils.basic import AnsibleModule

class Container():
    def __init__(self):
        # parameters
        self.module_args = dict(
            name=dict(type='str', required=True),
            version=dict(type='str', required=False),
            token=dict(type='str', required=False),
            check=dict(type='bool', required=False),
            state=dict(type='str', default='present', choices=['absent', 'present', 'latest', 'started', 'stopped']),
        )

        self.module = AnsibleModule(
            argument_spec=self.module_args,
            supports_check_mode=True
        )

        # skell to result
        self.result = self.module.params.copy()
        self.result['changed'] = False
        self.result['message'] = ''

        # check mode, don't made any changes
        #if self.module.check_mode:
        #    return self.result

        self.args = []

        if self.module.params['check']:
            self.args.append("-c")
        
        if self.module.params['version']:
            self.args.append("-v")
            self.args.append(self.module.params['version'])

        if self.module.params['token']:
            self.args.append("-t")
            self.args.append(self.module.params['token'])

        if self.module.params['state'] == 'present':
            self._import()

        if self.module.params['state'] == 'absent':
            self._destroy()

        if self.module.params['state'] == 'latest':
            self._update()

        if self.module.params['state'] == 'started':
            self._start()

        if self.module.params['state'] == 'stopped':
            self._stop()

    
    def _start(self):
        if self._is_running():
            self.result['changed'] = False
            self._exit()

        # verify if container is already installed
        if not self._is_installed():
            self.result['changed'] = True
            self.result['message'] = 'not installed'

            self._subutai_cmd("import")

            # try demote container
            self._subutai_cmd("demote")

            # try start container
            if self._subutai_cmd("start"):
                self._return_fail("Start Error")

            if self._is_running():
                self.result['changed'] = True

        else:
            # try demote container
            self._subutai_cmd("demote")

            # try start container
            if self._subutai_cmd("start"):
                self._return_fail("Start Error")

            if self._is_running():
                self.result['changed'] = True
            
        self._exit()

    def _stop(self):
        # verify if container is already installed
        if not self._is_installed():
            self.result['changed'] = True
            self.result['message'] = 'not installed'

            self._subutai_cmd("import")

            # try demote container
            self._subutai_cmd("demote")

            # try stop container
            if self._subutai_cmd("stop"):
                self._return_fail("Stop Error")

            if self._is_running():
                self.result['changed'] = True

        else:
            if not self._is_running():
                self.result['changed'] = False
                self._exit()
            # try demote container
            self._subutai_cmd("demote")

            # try start container
            if self._subutai_cmd("stop"):
                self._return_fail("Stop Error")

            if not self._is_running():
                self.result['changed'] = True
            
        self._exit()

    def _update(self):
        # verify if container is already installed
        if not self._is_installed():
            self.result['changed'] = True
            self.result['message'] = 'not installed'
            self._subutai_cmd("import")
            self._exit()

        else:
            self._subutai_cmd("demote")
            if self._subutai_cmd("start"):
                self._return_fail("Start Error")

            # try update container
            if self._subutai_cmd("update"):
                self._return_fail("Update Error")
            self.result['changed'] = True
            self._exit()

    def _destroy(self):
        if not self._is_installed():
            self.result['changed'] = False
            self._exit()
        else:
            # try destroy container
            if self._subutai_cmd("destroy"):
                self._return_fail("Destroy Error")
            self.result['changed'] = True
            self._exit()        
    
    def _import(self):
        # verify if container is already installed
        if self._is_installed():
            self.result['changed'] = False
            self.result['message'] = 'already installed'
        else:
            # try install container
            if self._subutai_cmd("import"):
                self._return_fail("Import Error")
            
            if self._is_installed():
                self.result['changed'] = True

        self._exit()

    def _exit(self):
        self.module.exit_json(**self.result)

    def _return_fail(self, err_msg):
        self.result['message'] = '[Err] ' + err_msg
        self.result['changed'] = False
        self.module.fail_json(msg='[Err] ' + err_msg, **self.result)

    def _is_installed(self):
        out = subprocess.Popen(
            ["/snap/bin/subutai", "list"], stdout=subprocess.PIPE).stdout.read()
        if self.module.params['name']+'\n' in out:
            return True
        else:
            return False

    def _is_running(self):
        out = subprocess.Popen(
            ["/snap/bin/subutai", "list", "-i", self.module.params['name']], stdout=subprocess.PIPE).stdout.read()
        if bytes("RUNNING") in out:
            return True
        else:
            return False

    def _subutai_cmd(self, cmd):
        err_msg = subprocess.Popen(
            ["/snap/bin/subutai", cmd, self.module.params['name']] + self.args, stderr=subprocess.PIPE).stderr.read()
        return err_msg

def main():
    c = Container()

if __name__ == '__main__':
    main()
