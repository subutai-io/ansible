#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'curated'
}

DOCUMENTATION = '''
---
module: subutai_migrate

short_description: subutai migrate module

version_added: "2.5"

description:
    - "migrate Subutai container"

options:
    container:
        description:
            - specifies required protocol for mapping and might be http, https, tcp or udp.
        required: true
    stage:
        description:
            - migration stage --  1, prepare-data ;  2, import-data ; 3, create-dump ; 4, restore-dump; 5, unfreeze
        required: true
    destination:
        description:
            - peer destination address
        required: true

extends_documentation_fragment:
    - subutai

author:
    - Fernando Silva (fsilva@optimal-dynamics.com)
'''

EXAMPLES = '''
# config container
  - name: migrate container to 192.168.0.2
    subutai_map:
      container: management
      stage: prepare-data
      destination: 192.168.0.2

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
        stage=dict(type='str', required=True),
        destination=dict(type='str', required=True),
    )

    # skell to result
    result = dict(
        changed=False,
        container='',
        stage='',
        destination='',
     )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # check mode, don't made any changes
    if module.check_mode:
        return result

    result['container'] = module.params['container']
    result['stage'] =  module.params['stage']
    result['destination'] = module.params['destination']

    args= ["/snap/bin/subutai","migrate"]
    args.append(module.params['container'])
    args.append("-s")
    args.append(module.params['stage'])
    args.append("-d")
    args.append(module.params['destination'])

    err = subprocess.Popen(args, stderr=subprocess.PIPE).stderr.read()
    if err:
        module.fail_json(msg='[Err] ' + err + str(args), **result)
    else:
        result['changed'] = True
        module.exit_json(**result)
        
def main():
    run_module()

if __name__ == '__main__':
    main()