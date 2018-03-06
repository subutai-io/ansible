#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: subutai_promote

short_description: Subutai promote module.

version_added: "2.6"

description:
    - Promotes container to template in subutai.

options:
    container:
        description:
            - Name of container.
        required: true
    source:
        description:
            - Set the source for promoting.

extends_documentation_fragment:
    - subutai

author:
    - Fernando Silva (@liquuid)
'''

EXAMPLES = '''
# promote template
- name: promote nginx template
  subutai_promote:
    container: nginx

'''

RETURN = '''
container:
    description: Container affected.
    type: str
message:
    description: The output message that the sample module generates.
'''

import subprocess
from ansible.module_utils.basic import AnsibleModule


def run_module():

    # parameters
    module_args = dict(
        container=dict(type='str', required=True),
        source=dict(type='str', required=False),
    )

    # skell to result
    result = dict(
        changed=False,
        source='',
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
    result['source'] = module.params['source']

    args = []
    if module.params['source']:
        args.append("-s")
        args.append(module.params['source'])

    if not is_promoted(module.params['container']):
        err = subprocess.Popen(
            ["/snap/bin/subutai", "promote", module.params['container']] + args, stderr=subprocess.PIPE).stderr.read()
        if err:
            result['changed'] = False
            module.fail_json(msg='[Err] ' + err, **result)
        result['changed'] = True

    else:
        result['changed'] = False
        result['message'] = "Already promoted"

    module.exit_json(**result)


def is_promoted(container):
    output = subprocess.Popen(
        ["/snap/bin/subutai", "list", "-t", container], stdout=subprocess.PIPE).stdout.read()
    if container in output:
        return True
    else:
        return False


def main():
    run_module()

if __name__ == '__main__':
    main()
