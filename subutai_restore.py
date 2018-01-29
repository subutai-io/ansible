#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'curated'
}

DOCUMENTATION = '''
---
module: subutai_restore

short_description: subutai restore module

version_added: "2.5"

description:
    - "restore containers in subutai"

options:
    backupname:
        description:
            - name of container
        required: true
    container:
        description:
            - name of new container
        required: false
    date:
        description:
            - date of backup to be restored
        required: false

extends_documentation_fragment
    - subutai

author:
    - Fernando Silva (fsilva@optimal-dynamics.com)
'''

EXAMPLES = '''
# restore container
- name: restore debian backup tp container
  subutai_restore:
    backupname: debian
    container: new_debian 

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
        backupname=dict(type='str', required=True),
        container=dict(type='str', required=True),
        date=dict(type='str', required=False),

    )

    # skell to result
    result = dict(
        changed=False,
        container='',
        backupname='',
        date='',
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
    result['backupname'] =  module.params['backupname']
    result['date'] = module.params['date']

    args=[]
    if module.params['date']:
        args.append("-d")
        args.append(module.params['date'])

    err = subprocess.Popen(["/snap/bin/subutai","restore", module.params['backupname'], "-c",  module.params['container']] + args , stderr=subprocess.PIPE).stderr.read()
    if err:
        result['changed'] = False
        module.fail_json(msg='[Err] ' + err, **result)

    result['changed'] = True
    result['message'] = err 
    module.exit_json(**result)

def get_config(container):
    return subprocess.Popen(["/snap/bin/subutai","config",container], stdout=subprocess.PIPE).stdout.read()

def main():
    run_module()

if __name__ == '__main__':
    main()