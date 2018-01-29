#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'curated'
}

DOCUMENTATION = '''
---
module: subutai_backup

short_description: subutai backup module

version_added: "2.5"

description:
    - "backup containers in subutai"

options:
    container:
        description:
            - name of container
        required: true
    full_backup:
        description:
            - make a full backup
        required: false
    stop_container:
        description:
            - stop container before backup
        required: false

extends_documentation_fragment
    - subutai

author:
    - Fernando Silva (fsilva@optimal-dynamics.com)
'''

EXAMPLES = '''
# backup container
- name: backup nginx container
  subutai_backup:
    container: nginx
    full_backup: true 
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
        full_backup=dict(type='bool', required=False),
        stop_container=dict(type='bool', required=False),
        
    )

    # skell to result
    result = dict(
        changed=False,
        container='',
        full_backup='',
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
    result['full_backup'] =  module.params['full_backup']
    result['stop_container'] = module.params['stop_container']

    args=[]
    if module.params['full_backup']:
        args.append("-f")
    
    if module.params['stop_container']:
        args.append("-s")

    err = subprocess.Popen(["/snap/bin/subutai","backup", module.params['container']] + args, stderr=subprocess.PIPE).stderr.read()
    if err:
        module.fail_json(msg='[Err] ' + err , **result)

    result['changed'] = True
      
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()