#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'curated'
}

DOCUMENTATION = '''
---
module: subutai_checkpoint

short_description: subutai checkpoint module

version_added: "2.5"

description:
    - "chekpoint/restore in user space"

options:
    container:
        description:
            - name of container
        required: true
    restore:
        description: 
            - Restore checkpoint
        required: false
    stop_container:
        description:
            - Stop container during checkpoint
        required: false

extends_documentation_fragment
    - subutai

author:
    - Fernando Silva (fsilva@optimal-dynamics.com)
'''

EXAMPLES = '''
# checkpoint container
- name: checkpoint nginx container
  subutai_checkpoint:
    container: nginx
    restore: false 
    stop_container: true

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
        restore=dict(type='bool', required=False),
        stop_container=dict(type='bool', required=False),
        
    )

    # skell to result
    result = dict(
        changed=False,
        container='',
        restore='',
        stop_container='', 
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
    result['restore'] =  module.params['restore']
    result['stop_container'] = module.params['stop_container']

    args=[]
    if module.params['restore']:
        args.append("-r")
    
    if module.params['stop_container']:
        args.append("-s")

    out = subprocess.Popen(["/snap/bin/subutai","checkpoint", module.params['container']] + args, stdout=subprocess.PIPE).stdout.read()
    
    if "Failed" in out:
        result['changed'] = False
        result['message'] = "/snap/bin/subutai checkpoint " + module.params['container'] +  str(args)
        module.fail_json(msg='[Err] ' + out, **result)
        
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()