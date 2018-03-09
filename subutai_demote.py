#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: subutai_demote

short_description: subutai demote module

version_added: "2.6"

description:
    - Demotes templates to containers in subutai.

options:
    container:
        description:
            - Name of container.
        required: true
    ipaddr:
        description:
            - IPv4 address, ie 192.168.1.1/24 

    vlan:
        description:
            - VLAN tag.

extends_documentation_fragment:
    - subutai

author:
    - Fernando Silva (@liquuid)
'''

EXAMPLES = '''
# demote template
- name: demote nginx template
  subutai_demote:
    container: nginx
    ipaddr: 192.168.1.1/24
    vlan: foo

'''

RETURN = '''
container:
    description: Container affected.
    type: string
    returned: always
    sample: "apache"
stderr:
    description: Error output from subutai demote
    type: string
    returned: success, when need
    sample: "ERRO[2018-03-09 00:15:56] Container management is not a template"
'''

import subprocess
from ansible.module_utils.basic import AnsibleModule


def run_module():

    # parameters
    module_args = dict(
        container=dict(type='str', required=True),
        ipaddr=dict(type='str', required=False),
        vlan=dict(type='str', required=False),
    )

    # skell to result
    result = dict(
        changed=False,
        container='',
        stderr=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # check mode, don't made any changes
    if module.check_mode:
        return result

    result['container'] = module.params['container']

    args = []
    if module.params['ipaddr']:
        args.append("-i")
        args.append(module.params['ipaddr'])

    if module.params['vlan']:
        args.append("-v")
        args.append(module.params['vlan'])

    if not is_demoted(module.params['container']):
        err = subprocess.Popen(
            ["/snap/bin/subutai", "demote", module.params['container']] + args, stderr=subprocess.PIPE).stderr.read()
        if err:
            result['changed'] = False
            result['stderr'] = err
            module.fail_json(msg='[Err] ' + err, **result)
        result['changed'] = True

    else:
        result['changed'] = False
        result['stderr'] = "Already demoted"

    module.exit_json(**result)


def is_demoted(container):
    output = subprocess.Popen(
        ["/snap/bin/subutai", "list", "-c", container], stdout=subprocess.PIPE).stdout.read()
    if container in output:
        return True
    else:
        return False


def main():
    run_module()

if __name__ == '__main__':
    main()
