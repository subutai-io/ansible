#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'curated'
}

DOCUMENTATION = '''
---
module: subutai_p2p

short_description: subutai p2p module

version_added: "2.5"

description:
    - "configure network p2p for containers in subutai"

options:
    command:
        description:
            - create, update, delete
        required: true
    interface:
        description:
            - Interface name
        required: false
    hash:
        description:
            - hash
        required: false
    key:
        description:
            - key
        required: false
    ttl:
        description:
            - ttl
        required: false
    localPeepIPAddr:
        description:
            - localPeepIPAddr
        required: false
    portrange :
        description:
            - portrange
        required: false


extends_documentation_fragment:
    - subutai

author:
    - Fernando Silva (fsilva@optimal-dynamics.com)
'''

EXAMPLES = '''
# p2p module
    - name: create p2p instance
      subutai_p2p:
        command: create
        interface: p2p-net1
        hash: swarm-12345678-abcd-1234-efgh-123456789012
        key: 0123456789qwertyu0123456789zxcvbn
        ttl: 1476870551
        localPeepIPAddr: 10.220.22.1
        portrange: 0-65535

      become: true
      register: testout
    - name: dump test output
      debug:
        msg: '{{ testout }}'

    - name: update p2p instance
      subutai_p2p:
        command: update
        interface: p2p-net1
        hash: swarm-12345678-abcd-1234-efgh-123456789012
        key: 0123456789qwertyu0123456789zxcvbn
        ttl: 1476870551

      become: true
      register: testout
    - name: dump test output
      debug:
        msg: '{{ testout }}'

    - name: delete p2p instance
      subutai_p2p:
        command: delete
        hash: swarm-12345678-abcd-1234-efgh-123456789012

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
from ansible.module_utils.basic import AnsibleModule


def run_module():

    # parameters
    module_args = dict(
        command=dict(type='str', required=True),
        interface=dict(type='str', required=False),
        hash=dict(type='str', required=False),
        key=dict(type='str', required=False),
        ttl=dict(type='str', required=False),
        localPeepIPAddr=dict(type='str', required=False),
        portrange=dict(type='str', required=False),

    )

    # skell to result
    result = dict(
        changed=False,
        command='',
        interface='',
        ttl='',
        localPeepIPAddr='',
        portrange='',

    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # check mode, don't made any changes
    if module.check_mode:
        return result

    result['command'] = module.params['command']
    result['interface'] = module.params['interface']
    result['hash'] = module.params['hash']
    result['key'] = module.params['key']
    result['ttl'] = module.params['ttl']
    result['localPeepIPAddr'] = module.params['localPeepIPAddr']
    result['portrange'] = module.params['portrange']

    args = ["/snap/bin/subutai", "p2p"]

    if module.params['command'] == "create":
        args.append("-c")
    elif module.params['command'] == "update":
        args.append("-u")
    elif module.params['command'] == "delete":
        args.append("-d")
    else:
        module.fail_json(msg='[Err] ' + str(args), **result)

    if module.params['interface']:
        args.append(module.params['interface'])

    if module.params['hash']:
        args.append(module.params['hash'])

    if module.params['key']:
        args.append(module.params['key'])

    if module.params['ttl']:
        args.append(module.params['ttl'])

    if module.params['localPeepIPAddr']:
        args.append(module.params['localPeepIPAddr'])

    if module.params['portrange']:
        args.append(module.params['portrange'])

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
