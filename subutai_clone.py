#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: subutai_clone

short_description: Subutai clone module.

version_added: "2.5"

description:
    - Clone containers in subutai.

options:
    parent:
        description:
            - Name of parent container.
        required: true
    child:
        description:
            - Name of child container.
        required: true
    env:
        description:
            - Set environment id for container.
        required: false
    ipaddr:
        description:
            - Set container IP address and VLAN.
        required: false
    token:
        description:
            - Token to verify with subutai's Bazaar.
        required: false
    kurjun_token:
        description:
            - Kurjun token to clone private and shared templates.
        required: false

extends_documentation_fragment:
    - subutai

author:
    - Fernando Silva (fsilva@optimal-dynamics.com)
'''

EXAMPLES = '''
# clone container
- name: clone nginx container
  subutai_clone:
    parent: nginx
    child: nginx2

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


def run_module():

    # parameters
    module_args = dict(
        parent=dict(type='str', required=True),
        child=dict(type='str', required=False),
        env=dict(type='str', required=False),
        ipaddr=dict(type='str', required=False),
        token=dict(type='str', required=False),
        kurjun_token=dict(type='str', required=False),

    )

    # skell to result
    result = dict(
        changed=False,
        parent='',
        env='',
        child='',
        ipaddr='',
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # check mode, don't made any changes
    if module.check_mode:
        return result

    result['parent'] = module.params['parent']
    result['child'] = module.params['child']
    result['env'] = module.params['env']
    result['ipaddr'] = module.params['ipaddr']
    result['token'] = module.params['token']
    result['kurjun_token'] = module.params['kurjun_token']

    args = []
    if module.params['env']:
        args.append("--env")
        args.append(module.params['env'])

    if module.params['ipaddr']:
        args.append("--ipaddr")
        args.append(module.params['ipaddr'])

    if module.params['token']:
        args.append("--token")
        args.append(module.params['token'])

    if module.params['kurjun_token']:
        args.append("--kurjun_token")
        args.append(module.params['kurjun_token'])

    if container_exists(module.params['child']):
        result['changed'] = False
        module.exit_json(**result)

    out = subprocess.Popen(["/snap/bin/subutai", "clone", module.params[
        'parent'], module.params['child']] + args, stderr=subprocess.PIPE).stderr.read()

    if out != "" or not container_exists(module.params['child']):
        result['changed'] = False
        result['message'] = out
        module.fail_json(msg='[Err] ' + out, **result)
    else:
        result['changed'] = True
        module.exit_json(**result)

def container_exists(container):
    out = subprocess.Popen(["/snap/bin/subutai", "list"], stdout=subprocess.PIPE).stdout.read()
    if container in out:
        return True
    else:
        return False


def main():
    run_module()

if __name__ == '__main__':
    main()
