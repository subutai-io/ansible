#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: subutai_quota

short_description: subutai quota module

version_added: "2.5"

description:
    - "set quotas for Subutai container"

options:
    container:
        description:
            - name of container
        required: true
    resource:
        description:
            - cpu, cpuset, ram, disk, network
        required: true
    set:
        description:
            - set quota for the specified resource
        required: true
    threshold:
        description:
            - set alert threshold
        required: true

extends_documentation_fragment:
    - subutai

author:
    - Fernando Silva (fsilva@optimal-dynamics.com)
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
        resource=dict(type='str', required=True),
        set=dict(type='str', required=True),
        threshold=dict(type='str', required=True),
    )

    # skell to result
    result = dict(
        changed=False,
        container='',
        resource='',
        set='',
        threshold='',
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
    result['resource'] = module.params['resource']
    result['set'] = module.params['set']
    result['threshold'] = module.params['threshold']

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
