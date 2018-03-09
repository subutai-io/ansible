#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: subutai_vxlan

short_description: Subutai vxlan module.

version_added: "2.6"

description:
    - Configure vxlan tunnels.

options:
    command:
        description:
            - create, delete
        required: true
    name:
        description:
            - Tunnel name.

    remoteip:
        description:
            - Remote IP address.

    vlan:
        description:
            - Vlan name.

    vni:
        description:
            - VXLAN tunnel VNI.

extends_documentation_fragment:
    - subutai

author:
    - Fernando Silva (@liquuid)
'''

EXAMPLES = '''
# vxlan module
  - name: adding subutai vxlan tunnel
    subutai_vxlan:
      command: create
      name: vxlan1
      remoteip: 10.220.22.2
      vlan: 100
      vni: 12345
    become: true
    register: testout

  - name: dump test output
    debug:
      msg: '{{ testout }}'

  - name: adding subutai vxlan tunnel
    subutai_vxlan:
      command: delete
      name: vxlan1
    become: true
    register: testout

  - name: dump test output
    debug:
      msg: '{{ testout }}'

'''

RETURN = '''
name:
    description: Name of vlan affected
    type: string
    returned: always
    sample: "vxlan1"
stderr:
    description: Error output from subutai vxlan
    type: string
    returned: success, when need
    sample: "Time Out"
'''

import subprocess
from ansible.module_utils.basic import AnsibleModule


def run_module():
    # parameters
    module_args = dict(
        command=dict(type='str', required=True, choices=['create', 'delete']),
        name=dict(type='str', required=True),
        remoteip=dict(type='str', required=False),
        vlan=dict(type='str', required=False),
        vni=dict(type='str', required=False)

    )

    # skell to result
    result = dict(
        changed=False,
        name=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # check mode, don't made any changes
    if module.check_mode:
        return result

    result['name'] = module.params['name']

    args = []

    if module.params['remoteip']:
        args.append("--remoteip")
        args.append(module.params['remoteip'])

    if module.params['vlan']:
        args.append("--vlan")
        args.append(module.params['vlan'])

    if module.params['vni']:
        args.append("--vni")
        args.append(module.params['vni'])

    if module.params['command'] == "create":
        err = subprocess.Popen(
            ["/snap/bin/subutai", "vxlan", "--create", module.params['name']] + args, stderr=subprocess.PIPE).stderr.read()
        if err:
            result['stderr'] = err
            module.fail_json(msg='[Err] ' + err + str(args), **result)
        else:
            if module.params['name'] in check_changes():
                result['changed'] = True
                module.exit_json(**result)
            else:
                module.fail_json(msg='[Err] ' + err + str(args), **result)

    elif module.params['command'] == "delete":
        err = subprocess.Popen(
            ["/snap/bin/subutai", "vxlan", "--delete", module.params['name']], stderr=subprocess.PIPE).stderr.read()
        if err:
            result['stderr'] = err
            module.fail_json(msg='[Err] ' + err, **result)
        else:
            if module.params['name'] not in check_changes():
                result['changed'] = True
                module.exit_json(**result)
            else:
                module.fail_json(msg='[Err] ' + err + str(args), **result)

    else:
        module.fail_json(msg='[Err] ' + str(args), **result)


def check_changes():
    return subprocess.Popen(["/snap/bin/subutai", "vxlan", "-l"], stdout=subprocess.PIPE).stdout.read()


def main():
    run_module()

if __name__ == '__main__':
    main()
