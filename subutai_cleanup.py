#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'curated'
}

DOCUMENTATION = '''
---
module: subutai_cleanup

short_description: subutai cleanup module

version_added: "2.5"

description:
    - "Cleanup subutai enviroment"

options:
    vlan:
        description:
            - name of vlan
        required: true

extends_documentation_fragment:
    - subutai

author:
    - Fernando Silva (fsilva@optimal-dynamics.com)
'''

EXAMPLES = '''
# cleanup enviroment
- name: cleanup enviroment
  subutai_cleanup:
    vlan: 101

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
        vlan=dict(type='str', required=True),
    )

    # skell to result
    result = dict(
        changed=False,
        vlan='',
        message=''
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
        result['changed'] = False
        module.fail_json(msg='[Err] ' + err, **result)

    result['changed'] = True

    module.exit_json(**result)


def main():
    run_module()

if __name__ == '__main__':
    main()
