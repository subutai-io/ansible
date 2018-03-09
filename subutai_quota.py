#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: subutai_quota

short_description: Subutai quota module.

version_added: "2.6"

description:
    - Set quotas for Subutai container.

options:
    container:
        description:
            - Name of container.
        required: true
    resource:
        description:
            - Cpu, cpuset, ram, disk, network.
        required: true
    set:
        description:
            - Set quota for the specified resource.
        required: true
    threshold:
        description:
            - Set alert threshold.
        required: true

extends_documentation_fragment:
    - subutai

author:
    - Fernando Silva (@liquuid)
'''

EXAMPLES = '''
# set quotas for container
- name: set quota nginx container
  subutai_quota:
    container: nginx
    resource: cpu
    set: 80
    threshold: 70

'''

RETURN = '''
container:
    description: Container affected.
    type: string
    returned: always
    sample: "apache"
'''

import subprocess
from ansible.module_utils.basic import AnsibleModule


def run_module():

    # parameters
    module_args = dict(
        container=dict(type='str', required=True),
        resource=dict(type='str', required=True, choices=['cpu', 'cpuset', 'ram', 'disk', 'network']),
        set=dict(type='str', required=True),
        threshold=dict(type='str', required=True),
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

    result['container'] = module.params['container']

    out = subprocess.Popen(
        ["/snap/bin/subutai", "quota", module.params['container'], module.params['resource'],
         "--set", module.params['set'], "--threshold",  module.params['threshold']], stdout=subprocess.PIPE).stdout.read()

    result['message'] = out
    result['changed'] = True

    module.exit_json(**result)


def main():
    run_module()

if __name__ == '__main__':
    main()
