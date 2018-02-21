#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'curated'
}

DOCUMENTATION = '''
---
module: subutai_hub

short_description: subutai register Peer to Hub module

version_added: "2.5"

description:
    - "register Peer to Hub"email=liquuid@gmail.com&peerName=rz12&password=******&peerScope=Public
requirements:
    - requests
options:
    command:
        description:
            - options are register, unregister
        required: true
    console:
        description:
            - The URL of subutai console to be registered
        required: true
    console_username:
        description:
            - Console username
        required: true
    console_password:
        description:
            - Console password
        required: true
    email:
        description:
            - Email registered on Hub
        required: false
    peer_name:
        description:
            - Name of Peer on hub
        required: false
    peer_scope:
        description:
            - options are Public, Private
        required: false
    hub_password:
        description:
            - Hub password
        required: false

extends_documentation_fragment:
    - subutai

author:
    - Fernando Silva (fsilva@optimal-dynamics.com)
'''

EXAMPLES = '''
# register peer module
    - name: register peer instance 
      subutai_hub:
        command: register
        console: https://192.168.0.100:9999
        console_username: admin
        console_password: secret
        email: example@example.com
        peer_name: peertest
        peer_scope: Public
        hub_password: ************

      become: true
      register: testout
    - name: dump test output
      debug:
        msg: '{{ testout }}'

    - name: unregister peer instance 
      subutai_hub:
        command: unregister
        console: https://192.168.0.100:9999
        console_username: admin
        console_password: secret

      become: true
      register: testout
    - name: dump test output
      debug:
        msg: '{{ testout }}'

'''

RETURN = '''
container:
    description: Container affected
    type: str
message:
    description: The output message that the sample module generates
'''

import subprocess
import requests
import urllib3
from ansible.module_utils.basic import AnsibleModule

def run_module():

    # parameters
    module_args = dict(
        command=dict(type='str', required=True),
        console=dict(type='str', required=True),
        console_username=dict(type='str', required=True),
        console_password=dict(type='str', required=True, no_log=True),
        email=dict(type='str', required=False),
        peer_name=dict(type='str', required=False),
        peer_scope=dict(type='str', required=False),
        hub_password=dict(type='str', required=False, no_log=True),
    )

    # skell to result
    result = dict(
        changed=False,
        message='',
        command='',
        console='',
        console_username='',
        email='',
        peer_name='',
        peer_scope='',
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # check mode, don't made any changes
    if module.check_mode:
        return result

    result['command'] = module.params['command']
    result['console'] = module.params['console']
    result['console_username'] = module.params['console_username']
    result['console_password'] = module.params['console_password']
    result['email'] = module.params['email']
    result['peer_name'] = module.params['peer_name']
    result['peer_scope'] = module.params['peer_scope']
    result['hub_password'] = module.params['hub_password']

    # disble annoying SSL warnings
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    s = requests.Session()
    s.post('{}/login'.format(module.params['console']), data={'username': module.params['username'], 'password': module.params['password']}, verify=False)
    
    if module.params['command'] == "register":
        s.post('{}/rest/v1/hub/register'.format(module.params['console']), data={'email': module.params['email'], 'peerName': module.params['peer_name'] , 'password': module.params['hub_password'] ,'peerScope': module.params['peer_scope'] }, verify=False)
        result['changed'] = True
        module.exit_json(**result)
    elif module.params['command'] == "unregister":
        s.post('{}/rest/v1/hub/unregister'.format(module.params['console']), verify=False)
        result['changed'] = True
        module.exit_json(**result)
    else:
        module.fail_json(msg='[Err] The options are register or unregister', **result)

def main():
    run_module()

if __name__ == '__main__':
    main()