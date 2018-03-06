#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: subutai_proxy

short_description: subutai proxy module

version_added: "2.5"

description:
    - "configure network proxy for containers in subutai"

options:
    command:
        description:
            - create, update, delete
        required: true
    vlan:
        description:
            - VLAN name
        required: false
    domain:
        description:
            - add domain to VLAN
        required: false
    host:
        description:
            - add host to domain on VLAN
        required: false
    policy:
        description:
            - set load balance policy (rr|lb|hash)
        required: false
    file:
        description:
            - pem certificate file
        required: false

extends_documentation_fragment:
    - subutai

author:
    - Fernando Silva (fsilva@optimal-dynamics.com)
'''

EXAMPLES = '''
# proxy module
  - name: add domain example.com to 100 vlan
    subutai_proxy:
      command: add
      vlan: 100
      domain: example.com
    become: true
    register: testout

  - name: dump test output
    debug:
      msg: '{{ testout }}'

  - name: add domain example.com to 100 vlan
    subutai_proxy:
      command: add
      vlan: 100
      host: 10.10.0.20
    become: true
    register: testout
  - name: dump test output
    debug:
      msg: '{{ testout }}'

  - name: delete domain example.com
    subutai_proxy:
      command: delete
      vlan: 100
      domain: example.com
    become: true
    register: testout

  - name: dump test output
    debug:
      msg: '{{ testout }}'

  - name: delete host 10.10.0.20
    subutai_proxy:
      command: delete
      vlan: 100
      host: 10.10.0.20
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
        vlan=dict(type='str', required=True),
        domain=dict(type='str', required=False),
        host=dict(type='str', required=False),
        policy=dict(type='str', required=False),
        file=dict(type='str', required=False),

    )

    # skell to result
    result = dict(
        changed=False,
        command='',
        vlan='',
        domain='',
        host='',
        policy='',
        message='',
        file='',
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # check mode, don't made any changes
    if module.check_mode:
        return result

    result['command'] = module.params['command']
    result['vlan'] = module.params['vlan']
    result['domain'] = module.params['domain']
    result['host'] = module.params['host']
    result['policy'] = module.params['policy']
    result['file'] = module.params['file']

    args = []
    check_args = []

    if module.params['domain']:
        args.append("--domain")
        args.append(module.params['domain'])
        check_args.append("-d")

    if module.params['host']:
        args.append("--host")
        args.append(module.params['host'])
        check_args.append("-h")
        check_args.append(module.params['host'])

    if module.params['policy']:
        args.append("--policy")
        args.append(module.params['policy'])

    if module.params['file']:
        args.append("--file")
        args.append(module.params['file'])

    if module.params['command'] == "add":
        out = subprocess.Popen(
            ["/snap/bin/subutai", "proxy", "check", module.params['vlan']] + check_args, stdout=subprocess.PIPE).stdout.read()
        if out:
            result['changed'] = False
            module.exit_json(**result)
        else:
            err = subprocess.Popen(
                ["/snap/bin/subutai", "proxy", "add", module.params['vlan']] + args, stderr=subprocess.PIPE).stderr.read()
            if err:
                module.fail_json(msg='[Err] ' + err + str(args), **result)
            else:
                result['changed'] = True
                module.exit_json(**result)

    elif module.params['command'] == "delete":
        err = subprocess.Popen(
            ["/snap/bin/subutai", "proxy", "del", module.params['vlan']] + check_args, stderr=subprocess.PIPE).stderr.read()
        if err:
            module.fail_json(msg='[Err] ' + err + str(args), **result)
        else:
            result['changed'] = True
            result['message'] = str(args)
            module.exit_json(**result)
    else:
        module.fail_json(msg='[Err] ' + str(args), **result)


def main():
    run_module()

if __name__ == '__main__':
    main()
