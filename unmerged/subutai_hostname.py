#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: subutai_hostname

short_description: Subutai hostname module

version_added: "2.6"

description:
    - Change hostname of container or host.

options:
    container:
        description:
            - Name of container.
        required: true
    newname:
        description:
            - Template version.
        required: true

extends_documentation_fragment:
    - subutai

author:
    - Fernando Silva (@liquuid)
'''

EXAMPLES = '''
# hostname container
- name: hostname debian container
  subutai_hostname:
    container: debian
    newname: debian-test

'''

RETURN = '''
container:
    description: Container affected.
    type: string
    returned: always
    sample: "apache"
newname:
    description: New hostname of container affected.
    type: string
    returned: always
    sample: "apache-new"
stderr:
    description: Error output from subutai hostname
    type: string
    returned: success, when need
    sample: "ERRO[2018-03-09 00:30:13] apache is not an container."
'''

import subprocess
from ansible.module_utils.basic import AnsibleModule


def run_module():

    # parameters
    module_args = dict(
        container=dict(type='str', required=True),
        newname=dict(type='str', required=True),

    )

    # skell to result
    result = dict(
        changed=False,
        container='',
        newname='',
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # check mode, don't made any changes
    if module.check_mode:
        return result

    result['container'] = module.params['container']
    result['newname'] = module.params['newname']

    err = subprocess.Popen(["/snap/bin/subutai", "hostname", module.params[
                           'container'], module.params['newname']], stderr=subprocess.PIPE).stderr.read()
    if err:
        result['changed'] = False
        result['stderr'] = err
        module.fail_json(msg='[Err] ' + err, **result)

    result['changed'] = True

    module.exit_json(**result)


def main():
    run_module()

if __name__ == '__main__':
    main()
