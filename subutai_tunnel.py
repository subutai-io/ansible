#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: subutai_tunnel

short_description: Subutai tunnel module.

version_added: "2.6"

description:
    - Configure network tunnel for containers in subutai.

options:
    command:
        description:
            - add, delete
        required: true
    ipaddr:
        description:
            - IP address.

    ttl:
        description:
            - Tunnels may also be set to be permanent (default) or temporary (ttl in seconds).

    globalFlag:
        description:
            - There are two types of channels - local (default), which is created from destination address to host and global from destination to Subutai Helper node.

extends_documentation_fragment:
    - subutai

author:
    - Fernando Silva (@liquuid)
'''

EXAMPLES = '''
# tunnel module
  - name: subutai tunnel add 10.10.0.20
    subutai_tunnel:
      command: add
      ipaddr: 10.10.0.20
    become: true
    register: testout

  - name: dump test output
    debug:
      msg: '{{ testout }}'

  - name: subutai tunnel add 10.10.0.30:8080 300 -g
    subutai_tunnel:
      command: add
      ipaddr: 10.10.0.30:8080
      ttl: 300
      globalFlag: true
    become: true
    register: testout

  - name: dump test output
    debug:
      msg: '{{ testout }}'

  - name: subutai tunnel del 10.10.0.30:8080
    subutai_tunnel:
      command: delete
      ipaddr: 10.10.0.30:8080
    become: true
    register: testout

  - name: dump test output
    debug:
      msg: '{{ testout }}'

  - name: subutai tunnel del 10.10.0.20:8080
    subutai_tunnel:
      command: delete
      ipaddr: 10.10.0.20:22
    become: true
    register: testout

  - name: dump test output
    debug:
      msg: '{{ testout }}'
'''

RETURN = '''
stderr:
    description: Error output from subutai tunnel
    type: string
    returned: success, when need
    sample: "ERRO[2018-03-09 01:42:20] Resolving nearest tunnel node address, lookup ssh.cdn.subutai.io on 192.168.0.1:53: read udp 192.168.0.112:50717->192.168.0.1:53: i/o timeout "
'''

import subprocess
from ansible.module_utils.basic import AnsibleModule


def run_module():
    # parameters
    module_args = dict(
        command=dict(type='str', required=True, choices=['add', 'delete']),
        ipaddr=dict(type='str', required=True),
        ttl=dict(type='str', required=False),
        globalFlag=dict(type='bool', required=False)

    )

    # skell to result
    result = dict(
        changed=False,

    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # check mode, don't made any changes
    if module.check_mode:
        return result

    args = []

    if module.params['ttl']:
        args.append(module.params['ttl'])

    if module.params['globalFlag']:
        args.append("-g")

    if module.params['command'] == "add":
        err = subprocess.Popen(
            ["/snap/bin/subutai", "tunnel", "add", module.params['ipaddr']] + args, stderr=subprocess.PIPE).stderr.read()
        if err:
            result['stderr'] = err
            module.fail_json(msg='[Err] ' + err + str(args), **result)
        else:
            result['changed'] = True
            module.exit_json(**result)

    elif module.params['command'] == "delete":
        err = subprocess.Popen(
            ["/snap/bin/subutai", "tunnel", "del", module.params['ipaddr']], stderr=subprocess.PIPE).stderr.read()
        if err:
            result['stderr'] = err
            module.fail_json(msg='[Err] ' + err, **result)
        else:
            result['changed'] = True
            module.exit_json(**result)
    else:
        module.fail_json(msg='[Err] ' + str(args), **result)


def main():
    run_module()

if __name__ == '__main__':
    main()
