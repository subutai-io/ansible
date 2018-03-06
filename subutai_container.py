#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'curated'
}

DOCUMENTATION = '''
---
module: subutai_container

short_description: subutai container module

version_added: "2.5"

description:
    - "This manage containers with subutai"

options:
    name:
        description:
            - name of container
        required: true
    state:
        description:
        - Indicates the desired container state are installed.
        default: present
        choices: [ absent, present ]
    version:
        description:
            - template version
        required: false
    token:
        description:
            - token to access private repo
        required: false

extends_documentation_fragment:
    - subutai

author:
    - Fernando Silva (fsilva@optimal-dynamics.com)
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
        name=dict(type='str', required=True),
        version=dict(type='str', required=False),
        token=dict(type='str', required=False),
        state=dict(type='str', default='present', choices=['absent', 'present']),
    )

    # skell to result
    result = dict(
        changed=False,
        name='',
        version='',
        message='',
        state='',
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # check mode, don't made any changes
    if module.check_mode:
        return result

    result['name'] = module.params['name']
    result['version'] = module.params['version']
    result['token'] = module.params['token']
    result['state'] = module.params['state']

    args = []
    
    if module.params['version']:
        args.append("-v")
        args.append(module.params['version'])

    if module.params['token']:
        args.append("-t")
        args.append(module.params['token'])

    if module.params['state'] == 'present':

        # verify if container is already installed
        if is_installed(module.params['name']):
            result['changed'] = False
            result['message'] = 'already installed'

        else:
            # try install container
            err_msg = subprocess.Popen(
                ["/snap/bin/subutai", "import", module.params['name']] + args, stderr=subprocess.PIPE).stderr.read()
            if err_msg:
                result['message'] = '[Err] ' + err_msg
                result['changed'] = False
                module.fail_json(msg='[Err] ' + err_msg, **result)

            if is_installed(module.params['name']):
                result['changed'] = True

        module.exit_json(**result)

    if module.params['state'] == 'absent':
        # verify if container is already installed
        if not is_installed(module.params['name']):
            result['changed'] = False
            result['message'] = 'not installed'
            module.exit_json(**result)

        else:
            # try destroy container
            err_msg = subprocess.Popen(
                ["/snap/bin/subutai", "destroy", module.params['name']], stderr=subprocess.PIPE).stderr.read()
            if err_msg:
                result['message'] = '[Err] ' + err_msg
                result['changed'] = False
                module.fail_json(msg='[Err] ' + err_msg, **result)
            else:
                result['changed'] = True
                module.exit_json(**result)

def is_installed(name):
    out = subprocess.Popen(
        ["/snap/bin/subutai", "list"], stdout=subprocess.PIPE).stdout.read()
    if name+'\n' in out:
        return True
    else:
        return False

def main():
    run_module()

if __name__ == '__main__':
    main()
