#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'curated'
}

DOCUMENTATION = '''
---
module: subutai_rename

short_description: subutai rename module

version_added: "2.5"

description:
    - "Rename of container or host"

options:
    container:
        description:
            - name of container
        required: true
    newname:
        description:
            - template version
        required: true

extends_documentation_fragment:
    - subutai

author:
    - Fernando Silva (fsilva@optimal-dynamics.com)
'''

EXAMPLES = '''
# rename container
- name: rename debian container
  subutai_rename:
    container: debian
    newname: debian-test 

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
        newname=dict(type='str', required=True),

    )

    # skell to result
    result = dict(
        changed=False,
        container='',
        newname='',
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # check mode, don't made any changes
    if module.check_mode:
        return result

    result['container'] = module.params['container']
    result['newname'] =  module.params['newname']

    err = subprocess.Popen(["/snap/bin/subutai","rename", module.params['container'], module.params['newname'] ], stderr=subprocess.PIPE).stderr.read()
    if err:
        result['changed'] = False
        module.fail_json(msg='[Err] ' + err, **result)

    result['changed'] = True
        
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()