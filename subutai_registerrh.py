#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'curated'
}

DOCUMENTATION = '''
---
module: subutai_registerrh

short_description: subutai register RH from Peer module

version_added: "2.5"

description:
    - "Peers with management installed can have Resource Hosts (RH) join the peer by being register."
requirements:
    - requests
options:
    command:
        description:
            - options are approve, remove
        required: true
    id:
        description:
            - ID is the UUID (PGP fingerprint) of the RH
        required: false
    console:
        description:
            - The URL of subutai console to be registered
        required: false
    username:
        description:
            - Console username
        required: false
    password:
        description:
            - Console password
        required: false

extends_documentation_fragment:
    - subutai

author:
    - Fernando Silva (fsilva@optimal-dynamics.com)
'''

EXAMPLES = '''
# register rh module
    - name: register rh instance
      subutai_registerrh:
        command: approve
        id: 9DBBA0ADFF947AF883ECBD93149F221EEE54C7YD
        console: https://192.168.0.100:9999
        username: admin
        password: secret

      become: true
      register: testout
    - name: dump test output
      debug:
        msg: '{{ testout }}'

    - name: register rh instance
      subutai_registerrh:
        command: remove
        id: 9DBBA0ADFF947AF883ECBD93149F221EEE54C7YD
        console: https://192.168.0.100:9999
        username: admin
        password: secret

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
        id=dict(type='str', required=True),
        console=dict(type='str', required=True),
        username=dict(type='str', required=True),
        password=dict(type='str', required=True, no_log=True),
    )

    # skell to result
    result = dict(
        changed=False,
        message='',
        command='',
        id='',
        console='',
        username='',
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # check mode, don't made any changes
    if module.check_mode:
        return result

    result['command'] = module.params['command']
    result['id'] = module.params['id']
    result['console'] = module.params['console']
    result['username'] = module.params['username']
    result['password'] = module.params['password']

    # disble annoying SSL warnings
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    s = requests.Session()
    s.post('{}/login'.format(module.params['console']), data={
           'username': module.params['username'], 'password': module.params['password']}, verify=False)

    if module.params['command'] == "approve":
        s.post('{}/rest/v1/registration/requests/{}/approve'.format(
            module.params['console'], module.params['id']), verify=False)
        result['changed'] = True
        module.exit_json(**result)
    elif module.params['command'] == "remove":
        s.post('{}/rest/v1/registration/requests/{}/remove'.format(
            module.params['console'], module.params['id']), verify=False)
        result['changed'] = True
        module.exit_json(**result)
    else:
        module.fail_json(
            msg='[Err] The options are approve or remove', **result)


def main():
    run_module()

if __name__ == '__main__':
    main()
