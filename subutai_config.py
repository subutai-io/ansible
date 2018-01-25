#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'curated'
}

DOCUMENTATION = '''
---
module: subutai_config

short_description: subutai config module

version_added: "2.5"

description:
    - "configure containers in subutai"

options:
    container:
        description:
            - name of container
        required: true
    operation:
        description:
            - <add|del> operation
        required: true
    key:
        description:
            - configuration key
        required: true
    value:
        description:
            - configuration value
        required: true

extends_documentation_fragment
    - subutai

author:
    - Fernando Silva (fsilva@optimal-dynamics.com)
'''

EXAMPLES = '''
# config container
- name: config nginx container
  subutai_config:
    container: nginx
    operation: add 
    key: foo
    value: bar

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
        operation=dict(type='str', required=True),
        key=dict(type='str', required=True),
        value=dict(type='str', required=True),
    )

    # skell to result
    result = dict(
        changed=False,
        container='',
        operation='',
        key='',
        value='',
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
    result['operation'] =  module.params['operation']
    result['key'] = module.params['key']
    result['value'] = module.params['value']


    if module.params['operation'] == "add":
        err = subprocess.Popen(["/snap/bin/subutai","config", module.params['container'], "-o","add", "--key",  module.params['key'],  "-v", module.params['value'] ], stderr=subprocess.PIPE).stderr.read()
        if err:
            module.fail_json(msg='[Err] ' + err, **result)

        out = get_config(module.params['container'])
        if module.params['key'] + " = " in out:
            result['changed'] = True
        else:
            result['changed'] = True
            result['message'] = "Key not found " + err
            module.fail_json(msg='[Err] key ' + module.params['key'] + ' not found', **result)
            
        
    elif module.params['operation'] == "del":
        initial_config = get_config(module.params['container'])
        if module.params['key'] + " = " in initial_config:
            post_config = subprocess.Popen(["/snap/bin/subutai","config", module.params['container'], "-o","del", "--key", module.params['key'],  "-v", module.params['value'] ], stderr=subprocess.PIPE).stderr.read()
            if module.params['key'] + " = " not in post_config:
                result['changed'] = True
            else:
                result['changed'] = False
                module.fail_json(msg='[Err] ' + module.params['operation'] + ' is not a valid operation', **result)
        else:
            result['changed'] = False
            result['message'] = "Key not found"
            module.fail_json(msg='[Err] key ' + module.params['key'] + ' not found', **result)
        
    else:
        result['changed'] = False
        result['message'] = "Valid operations are: add or del"
        module.fail_json(msg='[Err] ' + module.params['operation'] + ' is not a valid operation', **result)

    module.exit_json(**result)

def get_config(container):
    return subprocess.Popen(["/snap/bin/subutai","config",container], stdout=subprocess.PIPE).stdout.read()

def main():
    run_module()

if __name__ == '__main__':
    main()