#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: subutai_hub

short_description: Subutai register Peer to Hub module.

version_added: "2.6"

description:
    - Register Peer to Hub.
requirements:
    - requests
options:
    command:
        description:
            - Options are register, unregister.
        required: true
    console:
        description:
            - The URL of subutai console to be registered.
        required: true
    console_username:
        description:
            - Console username.
        required: true
    console_password:
        description:
            - Console password.
        required: true
    email:
        description:
            - Email registered on Hub.

    peer_name:
        description:
            - Name of Peer on hub.

    peer_scope:
        description:
            - Options are Public, Private.

    hub_password:
        description:
            - Hub password.


extends_documentation_fragment:
    - subutai
requirements:
    - python-requests (python 2)
    - python3-requests (python 3)

author:
    - Fernando Silva (@liquuid)
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
stderr:
    description: Error output from subutai hub
    type: string
    returned: success, when need
    sample: "500 internal server error"
'''

import subprocess
import requests
import urllib3
from ansible.module_utils.basic import AnsibleModule


def run_module():

    # parameters
    module_args = dict(
        command=dict(type='str', required=True, choices=['register', 'unregister']),
        console=dict(type='str', required=True),
        console_username=dict(type='str', required=True),
        console_password=dict(type='str', required=True, no_log=True),
        email=dict(type='str', required=False),
        peer_name=dict(type='str', required=False),
        peer_scope=dict(type='str', required=False, choices=['Public', 'Private']),
        hub_password=dict(type='str', required=False, no_log=True),
    )

    # skell to result
    result = dict(
        changed=False,
        message='',
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # check mode, don't made any changes
    if module.check_mode:
        return result

    result['command'] = module.params['command']

    # disble annoying SSL warnings
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    s = requests.Session()
    s.post('{}/login'.format(module.params['console']), data={'username': module.params[
           'console_username'], 'password': module.params['console_password']}, verify=False)

    if module.params['command'] == "register":
        result['message'] = s.post('{}/rest/v1/hub/register'.format(module.params['console']), data={'email': module.params['email'], 'peerName': module.params[
                                   'peer_name'], 'password': module.params['hub_password'], 'peerScope': module.params['peer_scope']}, verify=False).reason
        if result['message'] == "OK":
            result['changed'] = True
            module.exit_json(**result)
        else:
            result['stderr'] = result['message']
            result['changed'] = False
            module.fail_json(
                msg='[Err] {}'.format(result['message']), **result)

        result['changed'] = True
        module.exit_json(**result)
    elif module.params['command'] == "unregister":
        result['message'] = s.delete(
            '{}/rest/v1/hub/unregister'.format(module.params['console']), verify=False).reason
        if result['message'] == "OK":
            result['changed'] = True
            module.exit_json(**result)
        else:
            result['stderr'] = result['message']
            result['changed'] = False
            module.fail_json(
                msg='[Err] {}'.format(result['message']), **result)

        module.exit_json(**result)
    else:
        module.fail_json(
            msg='[Err] The options are register or unregister', **result)


def main():
    run_module()

if __name__ == '__main__':
    main()
