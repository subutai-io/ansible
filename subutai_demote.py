#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'curated'
}

DOCUMENTATION = '''
---
module: subutai_demote

short_description: subutai demote module

version_added: "2.5"

description:
    - "demotes templates to containers in subutai"

options:
    container:
        description:
            - name of container
        required: true
    ipaddr:
        description:
            - IPv4 address, ie 192.168.1.1/24
        required: false
    vlan:
        description:
            - VLAN tag
        required: false

extends_documentation_fragment
    - subutai

author:
    - Fernando Silva (fsilva@optimal-dynamics.com)
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
        ipaddr=dict(type='str', required=False),
        vlan=dict(type='str', required=False),
    )

    # skell to result
    result = dict(
        changed=False,
        container='',
        ipaddr='',
        vlan='',
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
    result['ipaddr'] =  module.params['ipaddr']
    result['vlan'] = module.params['vlan']

    args= ""
    if module.params['ipaddr']:
        args += " -i " + module.params['ipaddr']
    
    if module.params['vlan']:
        args += " -v " + module.params['vlan']

    if not is_demoted(module.params['container']):
        err = subprocess.Popen(["/snap/bin/subutai","demote",module.params['container'], args ], stderr=subprocess.PIPE).stderr.read()
        if err:
            result['changed'] = False
            module.fail_json(msg='[Err] ' + err, **result)
        result['changed'] = True
  
    else:
        result['changed'] = False
        result['message'] = "Already demoted" 
        
    
    module.exit_json(**result)

def is_demoted(container):
    output = subprocess.Popen(["/snap/bin/subutai","list","-c",container], stdout=subprocess.PIPE).stdout.read()
    if container in output:
        return True
    else:
        return False

def main():
    run_module()

if __name__ == '__main__':
    main()