#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'curated'
}

DOCUMENTATION = '''
---
module: subutai_update

short_description: subutai update module

version_added: "2.5"

description:
    - "update containers in subutai"

options:
    container:
        description:
            - name of container
        required: true
    check:
        description:
            - check for updates without installation
        required: false

extends_documentation_fragment:
    - subutai

author:
    - Fernando Silva (fsilva@optimal-dynamics.com)
'''

EXAMPLES = '''
# update container
- name: update nginx container
  subutai_update:
    container: nginx

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
        check=dict(type='bool', required=False),
              
    )

    # skell to result
    result = dict(
        changed=False,
        container='',
        check='',
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
    result['check'] =  module.params['check']

    args= ""
    if module.params['check']:
        args += " -c"
    
    out = subprocess.Popen(["/snap/bin/subutai","update", module.params['container'], args ], stdout=subprocess.PIPE).stdout.read()
    
    result['changed'] = True

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()