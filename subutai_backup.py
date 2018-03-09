#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: subutai_backup

short_description: subutai backup module

version_added: "2.6"

description:
    - Backup containers in subutai.

options:
    container:
        description:
            - The name of container.
        required: true
    full_backup:
        description:
            - Make a full backup.

    stop_container:
        description:
            - Stop container before backup.

extends_documentation_fragment:
    - subutai

author:
    - Fernando Silva (@liquuid)
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
    description: Container affected.
    type: string
    returned: always
    sample: "apache"
full_backup:
    description: If full backup was requested or not
    type: boolean
    returned: success, when need
    sample: True
stop_container:
    description: If a stopped container was requested or not
    type: boolean
    returned: success, when need
    sample: True
stderr:
    description: Error output from subutai backup
    type: string
    returned: success, when need
    sample: "FATA[2018-03-08 22:09:42] Last backup not found or corrupted. Try make full backup."
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
        stderr=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # check mode, don't made any changes
    if module.check_mode:
        return result

    result['container'] = module.params['container']
    result['full_backup'] = module.params['full_backup']
    result['stop_container'] = module.params['stop_container']

    args = []
    if module.params['full_backup']:
        args.append("-f")

    if module.params['stop_container']:
        args.append("-s")

    err = subprocess.Popen(
        ["/snap/bin/subutai", "backup", module.params['container']] + args, stderr=subprocess.PIPE).stderr.read()
    if err:
        result['stderr'] = err
        module.fail_json(msg='[Err] ' + err, **result)

    result['changed'] = True

    module.exit_json(**result)


def main():
    run_module()

if __name__ == '__main__':
    main()
