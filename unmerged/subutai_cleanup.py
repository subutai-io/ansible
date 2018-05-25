#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: subutai_cleanup

short_description: Subutai cleanup module.

version_added: "2.6"

description:
    - Cleanup subutai enviroment.

options:
    vlan:
        description:
            - Name of vlan.
        required: true

extends_documentation_fragment:
    - subutai

author:
    - Fernando Silva (@liquuid)
'''

EXAMPLES = '''
# cleanup enviroment
- name: cleanup enviroment
  subutai_cleanup:
    vlan: 101

'''

RETURN = '''
vlan:
    description: VLAN affected.
    type: string
    returned: always
    sample: "101"
stderr:
    description: Error output from subutai cleanup
    type: string
    returned: success, when need
    sample: "INFO[2018-03-08 23:41:05] 111 not found. Please check if the name is correct"
'''

import subprocess
from ansible.module_utils.basic import AnsibleModule


def run_module():

    # parameters
    module_args = dict(
        vlan=dict(type='str', required=True),
    )

    # skell to result
    result = dict(
        changed=False,
        vlan='',
        stderr=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    # check mode, don't made any changes
    if module.check_mode:
        return result

    result['vlan'] = module.params['vlan']

    # verify if container is already started
    err = subprocess.Popen(
        ["/snap/bin/subutai", "cleanup",  module.params['vlan']], stderr=subprocess.PIPE).stderr.read()
    if err:
        result['stderr'] = err
        module.fail_json(msg='[Err] ' + err, **result)

    result['changed'] = True

    module.exit_json(**result)


def main():
    run_module()

if __name__ == '__main__':
    main()
