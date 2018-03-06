#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: subutai_export

short_description: Subutai export module.

version_added: "2.5"

description:
    - Export containers in subutai.

options:
    container:
        description:
            - Name of container.
        required: true
    version:
        description:
            - Template version.

    size:
        description:
            - Template preferred size -- tiny, small, medium, large, huge.

    token:
        description:
            - token to access private repo

    description:
        description:
            - template description

    private:
        description:
            - use private repo for uploading template


extends_documentation_fragment:
    - subutai

author:
    - Fernando Silva (fsilva@optimal-dynamics.com)
'''

EXAMPLES = '''
# export container
- name: export debian container
  subutai_export:
    container: debian
    size: tiny
    description: foo bar

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
        version=dict(type='str', required=False),
        size=dict(type='str', required=False, choices=['tiny', 'small', 'medium', 'large', 'huge']),
        token=dict(type='str', required=False),
        description=dict(type='str', required=False),
        private=dict(type='bool', required=False),
    )

    # skell to result
    result = dict(
        changed=False,
        container='',
        version='',
        size='',
        description='',
        private='',
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
    result['version'] = module.params['version']
    result['size'] = module.params['size']
    result['token'] = module.params['token']
    result['description'] = module.params['description']
    result['private'] = module.params['private']

    args = []

    if module.params['version']:
        args.append("-v")
        args.append(module.params['version'])

    if module.params['size']:
        args.append("-s")
        args.append(module.params['size'])

    if module.params['token']:
        args.append("-t")
        args.append(module.params['token'])

    if module.params['description']:
        args.append("-d")
        args.append(module.params['description'])

    if module.params['private']:
        args.append("-p")
        args.append(str(module.params['private']))

    err = subprocess.Popen(
        ["/snap/bin/subutai", "export", module.params['container']] + args, stderr=subprocess.PIPE).stderr.read()
    if err:
        result['changed'] = False
        module.fail_json(msg='[Err] ' + err, **result)

    result['changed'] = True

    module.exit_json(**result)


def main():
    run_module()

if __name__ == '__main__':
    main()
