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

extends_documentation_fragment
    - subutai

author:
    - Fernando Silva (fsilva@optimal-dynamics.com)
'''

EXAMPLES = '''
# cleanup enviroment
- name: cleanup enviroment
  subutai_cleanup:
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

    # skell to result
    result = dict(
        changed=False,
        message=''
    )

    module = AnsibleModule(
        argument_spec=dict(),
        supports_check_mode=True,
    )

    # check mode, don't made any changes
    if module.check_mode:
        return result

    # verify if container is already started
    out = subprocess.Popen(["/snap/bin/subutai","cleanup"], stdout=subprocess.PIPE).stdout.read()
    result['changed'] = True

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()