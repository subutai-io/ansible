#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: subutai_map

short_description: Subutai map module.

version_added: "2.5"

description:
    - Configure network map for containers in subutai.

options:
    protocol:
        description:
            - Specifies required protocol for mapping and might be http, https, tcp or udp.
        required: true
    internal:
        description:
            - Peer's internal socket that should be exposed. Format should be <ip>:<port>
        required: false
    external:
        description:
            - Optional parameter which shows desired RH socket where internal socket should be mapped. If more than one container mapped to one RH port, those containers are being put to the same backend group. Allowed port value must be in range of 1000-65535
        required: false
    domain:
        description:
            - Should be only specified for http and https protocols mapping.
        required: false
    cert:
        description:
            - Path to SSL pem certificate for https protocol.
        required: false
    policy:
        description:
            - Balancing methods (round-robin by default, least_time, hash, ip_hash).
        required: false
    sslbackend :
        description:
            - SSL backend in https upstream.
        required: false
    remove:
        description:
            - Optional flags shows that specified mapping should be removed. If not set, "add" operation is assumed.
        required: false

extends_documentation_fragment:
    - subutai

author:
    - Fernando Silva (fsilva@optimal-dynamics.com)
'''

EXAMPLES = '''
# config map
  - name: map container's 172.16.31.3 port 3306 to the random port on RH
    subutai_map:
      protocol: tcp
      internal: 172.16.31.3:3306

  - name: add 172.16.31.4:3306 to the same group
    subutai_map:
      protocol: tcp
      internal: 172.16.31.4:3306
      external: 46558

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
        protocol=dict(type='str', required=True, choices=['http', 'https', 'tcp', 'udp']),
        internal=dict(type='str', required=False),
        external=dict(type='str', required=False),
        domain=dict(type='str', required=False),
        cert=dict(type='str', required=False),
        policy=dict(type='str', required=False),
        sslbackend=dict(type='str', required=False),
        remove=dict(type='bool', required=False),
    )

    # skell to result
    result = dict(
        changed=False,
        protocol='',
        internal='',
        external='',
        domain='',
        cert='',
        policy='',
        sslbackend='',
        remove=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # check mode, don't made any changes
    if module.check_mode:
        return result

    result['protocol'] = module.params['protocol']
    result['internal'] = module.params['internal']
    result['external'] = module.params['external']
    result['domain'] = module.params['domain']
    result['cert'] = module.params['cert']
    result['policy'] = module.params['policy']
    result['sslbackend'] = module.params['sslbackend']
    result['remove'] = module.params['remove']

    args = ["/snap/bin/subutai", "map"]
    args.append(module.params['protocol'])
    if module.params['internal']:
        args.append("--internal")
        args.append(module.params['internal'])

    if module.params['external']:
        args.append("--external")
        args.append(module.params['external'])

    if module.params['domain']:
        args.append("--domain")
        args.append(module.params['domain'])

    if module.params['cert']:
        args.append("--cert")
        args.append(module.params['cert'])

    if module.params['policy']:
        args.append("--policy")
        args.append(module.params['policy'])

    if module.params['remove']:
        args.append("--remove")
        args.append(module.params['remove'])

    if module.params['sslbackend']:
        args.append("--sslbackend")
        args.append(module.params['sslbackend'])

    err = subprocess.Popen(args, stderr=subprocess.PIPE).stderr.read()
    if err:
        if "already exists" in err:
            result['changed'] = False
            module.exit_json(**result)
        else:
            module.fail_json(msg='[Err] ' + err + str(args), **result)
    else:
        result['changed'] = True
        module.exit_json(**result)


def main():
    run_module()

if __name__ == '__main__':
    main()
