#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'curated'
}

DOCUMENTATION = '''
---
module: subutai_start

short_description: subutai start module

version_added: "2.5"

description:
    - "Start containers to subutai"

options:
    container:
        description:
            - name of container
        required: true

extends_documentation_fragment:
    - subutai

author:
    - Fernando Silva (fsilva@optimal-dynamics.com)
'''

EXAMPLES = '''
# Start container
- name: Start management container
  subutai_start:
    container: management

'''

RETURN = '''
container:
    description: Container affected
    type: str
message:
    description: The output message that the sample module generates
'''

import subprocess
from ansible.module_utils.basic import AnsibleModule


def run_module():

    # parameters
    module_args = dict(
        container=dict(type='str', required=True),
    )

    # skell to result
    result = dict(
        changed=False,
        container='',
        message=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # check mode, don't made any changes
    if module.check_mode:
        return result

    result['container'] = module.params['container']

    # verify if container is already started
    if is_running(module.params['container']):
        result['changed'] = False
        result['message'] = 'already started'

    else:
        # try start container
        err_msg = subprocess.Popen(
            ["/snap/bin/subutai", "start", module.params['container']], stderr=subprocess.PIPE).stderr.read()
        if err_msg:
            result['message'] = '[Err] ' + err_msg
            result['changed'] = False
            module.fail_json(msg='[Err] ' + err_msg, **result)

        if is_running(module.params['container']):
            result['changed'] = True

    module.exit_json(**result)

def is_running(container):
    out = subprocess.Popen(
        ["/snap/bin/subutai", "list", "-i", container], stdout=subprocess.PIPE).stdout.read()
    if bytes("RUNNING") in out:
        return True
    else:
        return False


def main():
    run_module()

if __name__ == '__main__':
    main()
