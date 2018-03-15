#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: subutai_container

short_description: subutai container module

version_added: "2.6"

description:
    - This modules manage all life cicle of subutai containers.

options:
    name:
        description:
            - Name of container.
    network:
        description:
            - Define network operations, like: Configuring network tunnel for containers in subutai, vxlan tunnels, p2p configurations and network maps.
        choices: [ tunnel, vxlan, map, p2p ]
    state:
        description:
        - Indicates the desired container state are installed.
        default: present
        choices: [ absent, demote, promote, present, latest, started, stopped ]
    version:
        description:
            - Template version.

    token:
        description:
            - Token to access private repo.

    check:
        description:
            - Check for updates without installation.

    source:
        description:
            - Set the source for promoting.

    ipaddr:
        description:
            - IPv4 address, ie 192.168.1.1/24 

    vlan:
        description:
            - VLAN tag.

    ttl:
        description:
            - Tunnels may also be set to be permanent (default) or temporary (ttl in seconds).

    globalFlag:
        description:
            - There are two types of channels - local (default), which is created from destination address to host and global from destination to Subutai Helper node.
    
    protocol:
        description:
            - Specifies required protocol for mapping and might be http, https, tcp or udp.

    internal:
        description:
            - Peer's internal socket that should be exposed. Format should be <ip>:<port>

    external:
        description:
            - Optional parameter which shows desired RH socket where internal socket should be mapped. If more than one container mapped to one RH port, those containers are being put to the same backend group. Allowed port value must be in range of 1000-65535

    domain:
        description:
            - Should be only specified for http and https protocols mapping.

    cert:
        description:
            - Path to SSL pem certificate for https protocol.

    policy:
        description:
            - Balancing methods (round-robin by default, least_time, hash, ip_hash).

    sslbackend :
        description:
            - SSL backend in https upstream.

extends_documentation_fragment:
    - subutai

author:
    - Fernando Silva (@liquuid)
'''

EXAMPLES = '''

- name: run subutai import nginx
    subutai_container:
    name: nginx
    state: present
    become: true

- name: run subutai destroy nginx
    subutai_container:
    name: nginx
    state: absent
    become: true

- name: upgrade nginx
    subutai_container:
    name: nginx
    state: latest
    become: true

- name: promote nginx template
  subutai_container:
    state: promote
    name: nginx
    
- name: demote nginx template
  subutai_container:
    name: nginx
    state: demote
    ipaddr: 192.168.1.1/24
    vlan: foo

- name: subutai tunnel add 10.10.0.20
    subutai_container:
        network: tunnel
        state: present
        ipaddr: 10.10.0.20

- name: subutai tunnel add 10.10.0.30:8080 300 -g
    subutai_container:
        network: tunnel
        state: present
        ipaddr: 10.10.0.30:8080
        ttl: 300
        globalFlag: true

- name: subutai tunnel del 10.10.0.30:8080
    subutai_container:
        network: tunnel
        state: absent
        ipaddr: 10.10.0.30:8080

- name: subutai tunnel del 10.10.0.20:8080
    subutai_container:
        network: tunnel
        state: absent
        ipaddr: 10.10.0.20:22

- name: map container's 172.16.31.3 port 3306 to the random port on RH
    subutai_container:
    network: map
    state: present
    protocol: tcp
    internal: 172.16.31.3:3306 

- name: add 172.16.31.4:3306 to the same group
    subutai_container:
    network: map
    state: present
    protocol: tcp
    internal: 172.16.31.4:3306
    external: 46558

- name: remove container 172.16.31.3 from mapping
    subutai_container:
    network: map
    state: absent
    protocol: tcp
    internal: 172.16.31.3:3306
    external: 46558

- name: map 172.16.25.12:80 to RH's 8080 with domain name example.com
    subutai_container:
    network: map
    state: present
    protocol: http
    internal: 172.16.25.12:80
    external: 8080
    domain: example.com

- name: add container to existing example.com domain
    subutai_container:
    network: map
    state: present
    protocol: http
    internal: 172.16.25.13:80
    external: 8080
    domain: example.com
'''

RETURN = '''
container:
    description: Container affected.
    type: string
    returned: always
    sample: "apache"
stderr:
    description: Error output from subutai container
    type: string
    returned: success, when need
    sample: "FATA[2018-03-09 00:10:29] Extracting tgz, read /var/snap/subutai/common/lxc/tmpdir/: is a directory"
'''

import subprocess
from ansible.module_utils.basic import AnsibleModule

class Container():
    def __init__(self):
        # parameters
        self.module_args = dict(
            name=dict(type='str', required=False),
            network=dict(type='str', choices=['tunnel', 'map']),
            source=dict(type='str', required=False),
            version=dict(type='str', required=False),
            token=dict(type='str', required=False),
            check=dict(type='bool', required=False),
            ipaddr=dict(type='str', required=False),
            vlan=dict(type='str', required=False),
            ttl=dict(type='str', required=False),
            globalFlag=dict(type='bool', required=False),
            state=dict(type='str', default='present', choices=['absent', 'demote', 'present', 'promote', 'latest', 'started', 'stopped']),
            protocol=dict(type='str', required=False, choices=['http', 'https', 'tcp', 'udp']),
            internal=dict(type='str', required=False),
            external=dict(type='str', required=False),
            domain=dict(type='str', required=False),
            cert=dict(type='str', required=False),
            policy=dict(type='str', required=False, choices=['round-robin', 'least_time', 'hash', 'ip_hash']),
            sslbackend=dict(type='str', required=False),
        )

        self.module = AnsibleModule(
            argument_spec=self.module_args,
            supports_check_mode=True,
            required_one_of=[['name', 'network']],
            required_if=[
                [ "network", "tunnel", [ "ipaddr" ] ],
                [ "network", "map", [ "protocol" ] ],
            ]
        )

        # skell to result
        self.result = self.module.params.copy()
        self.result['changed'] = False
        self.result['message'] = ''

        # check mode, don't made any changes
        if self.module.check_mode:
            self._exit()

        self.args = []

        if self.module.params['check']:
            self.args.append("-c")
        
        if self.module.params['version']:
            self.args.append("-v")
            self.args.append(self.module.params['version'])

        if self.module.params['token']:
            self.args.append("-t")
            self.args.append(self.module.params['token'])

        if self.module.params['name']:

            if self.module.params['state'] == 'present':
                self._import()

            if self.module.params['state'] == 'promote':
                self._promote()

            if self.module.params['state'] == 'demote':
                self._demote()

            if self.module.params['state'] == 'absent':
                self._destroy()

            if self.module.params['state'] == 'latest':
                self._update()

            if self.module.params['state'] == 'started':
                self._start()

            if self.module.params['state'] == 'stopped':
                self._stop()

        if self.module.params['network'] == 'tunnel':
            self._tunnel()

        if self.module.params['network'] == 'map':
            self._map()
    
    def _start(self):
        if self._is_running():
            self.result['changed'] = False
            self._exit()

        # verify if container is already installed
        if not self._is_installed():
            self.result['changed'] = True
            self.result['message'] = 'not installed'

            self._subutai_cmd("import")

            # try demote container
            self._subutai_cmd("demote")

            # try start container
            if self._subutai_cmd("start"):
                self._return_fail("Start Error")

            if self._is_running():
                self.result['changed'] = True

        else:
            # try demote container
            self._subutai_cmd("demote")

            # try start container
            if self._subutai_cmd("start"):
                self._return_fail("Start Error")

            if self._is_running():
                self.result['changed'] = True
            
        self._exit()

    def _stop(self):
        # verify if container is already installed
        if not self._is_installed():
            self.result['changed'] = True
            self.result['message'] = 'not installed'

            self._subutai_cmd("import")

            # try demote container
            self._subutai_cmd("demote")

            # try stop container
            if self._subutai_cmd("stop"):
                self._return_fail("Stop Error")

            if self._is_running():
                self.result['changed'] = True

        else:
            if not self._is_running():
                self.result['changed'] = False
                self._exit()
            # try demote container
            self._subutai_cmd("demote")

            # try start container
            if self._subutai_cmd("stop"):
                self._return_fail("Stop Error")

            if not self._is_running():
                self.result['changed'] = True
            
        self._exit()

    def _update(self):
        # verify if container is already installed
        if not self._is_installed():
            self.result['changed'] = True
            self.result['message'] = 'not installed'
            self._subutai_cmd("import")
            self._exit()

        else:
            self._subutai_cmd("demote")
            if self._subutai_cmd("start"):
                self._return_fail("Start Error")

            # try update container
            if self._subutai_cmd("update"):
                self._return_fail("Update Error")
            self.result['changed'] = True
            self._exit()

    def _destroy(self):
        if not self._is_installed():
            self.result['changed'] = False
            self._exit()
        else:
            # try destroy container
            if self._subutai_cmd("destroy"):
                self._return_fail("Destroy Error")
            self.result['changed'] = True
            self._exit()        
    
    def _import(self):
        # verify if container is already installed
        if self._is_installed():
            self.result['changed'] = False
            self.result['message'] = 'already installed'
        else:
            # try install container
            if self._subutai_cmd("import"):
                self._return_fail("Import Error")
            
            if self._is_installed():
                self.result['changed'] = True

        self._exit()

    def _promote(self):
        if self.module.params['source']:
            self.args.append("-s")
            self.args.append(self.module.params['source'])

        if not self._is_promoted():
            err = subprocess.Popen(
                ["/snap/bin/subutai", "promote", self.module.params['name']] + self.args, stderr=subprocess.PIPE).stderr.read()
            if err:
                self.result['changed'] = False
                self.result['stderr'] = err
                self._return_fail(err)
            self.result['changed'] = True

        else:
            self.result['changed'] = False
            self.result['stderr'] = "Already promoted"

        self._exit()

    def _demote(self):
        if self.module.params['ipaddr']:
            self.args.append("-i")
            self.args.append(self.module.params['ipaddr'])

        if self.module.params['vlan']:
            self.args.append("-v")
            self.args.append(self.module.params['vlan'])

        if not self._is_demoted():
            err = subprocess.Popen(
                ["/snap/bin/subutai", "demote", self.module.params['name']] + self.args, stderr=subprocess.PIPE).stderr.read()
            if err:
                self.result['changed'] = False
                self.result['stderr'] = err
                self._return_fail(err)
            self.result['changed'] = True

        else:
            self.result['changed'] = False
            self.result['stderr'] = "Already demoted"

        self._exit()

    def _tunnel(self):
        if self.module.params['ttl']:
            self.args.append(self.module.params['ttl'])

        if self.module.params['globalFlag']:
            self.args.append("-g")

        if self.module.params['state'] == "present":
            if not self._exists_tunnel():
                err = subprocess.Popen(
                    ["/snap/bin/subutai", "tunnel", "add", self.module.params['ipaddr']] + self.args, stderr=subprocess.PIPE).stderr.read()
                if err:
                    self.result['stderr'] = err
                    self._return_fail(err)
                else:
                    self.result['changed'] = True
                    self._exit()
            else:
                self.result['changed'] = False
                self.result['stderr'] = "Tunnel already exist"
                self._exit()

        elif self.module.params['state'] == "absent":
            if self._exists_tunnel():
                err = subprocess.Popen(
                    ["/snap/bin/subutai", "tunnel", "del", self.module.params['ipaddr']], stderr=subprocess.PIPE).stderr.read()
                if err:
                    self.result['stderr'] = err
                    self._return_fail(err)
                else:
                    self.result['changed'] = True
                    self._exit()
            else:
                self.result['changed'] = False
                self.result['stderr'] = "Tunnel do not exist"
                self._exit()

        else:
            self._return_fail(err)

    def _map(self):
        self.args.append(self.module.params['protocol'])
        if self.module.params['internal']:
            self.args.append("--internal")
            self.args.append(self.module.params['internal'])

        if self.module.params['external']:
            self.args.append("--external")
            self.args.append(self.module.params['external'])

        if self.module.params['domain']:
            self.args.append("--domain")
            self.args.append(self.module.params['domain'])

        if self.module.params['cert']:
            self.args.append("--cert")
            self.args.append(self.module.params['cert'])

        if self.module.params['policy']:
            self.args.append("--policy")
            self.args.append(self.module.params['policy'])

        if self.module.params['sslbackend']:
            self.args.append("--sslbackend")
            self.args.append(self.module.params['sslbackend'])

        if self.module.params['state'] == 'absent':
            self.args.append("--remove")

        err = subprocess.Popen(["/snap/bin/subutai", "map" ,  self.module.params['protocol']] + self.args, stderr=subprocess.PIPE).stderr.read()
        if err:
            if "already exists" in err:
                self.result['changed'] = False
                self._exit()
            else:
                self.result['stderr'] = err
                self._return_fail(err)
        else:
            self.result['changed'] = True
            self._exit()


    def _exit(self):
        self.module.exit_json(**self.result)

    def _return_fail(self, err_msg):
        self.result['stderr'] = err_msg
        self.result['changed'] = False
        self.module.fail_json(msg='[Err] ' + err_msg, **self.result)

    def _is_installed(self):
        out = subprocess.Popen(
            ["/snap/bin/subutai", "list"], stdout=subprocess.PIPE).stdout.read()
        if self.module.params['name']+'\n' in out:
            return True
        else:
            return False

    def _exists_tunnel(self):
        out = subprocess.Popen(
            ["/snap/bin/subutai", "tunnel", "list"], stdout=subprocess.PIPE).stdout.read()
        if self.module.params['ipaddr'] in out:
            return True
        else:
            return False

    def _is_running(self):
        out = subprocess.Popen(
            ["/snap/bin/subutai", "list", "-i", self.module.params['name']], stdout=subprocess.PIPE).stdout.read()
        if bytes("RUNNING") in out:
            return True
        else:
            return False

    def _is_promoted(self):
        output = subprocess.Popen(
            ["/snap/bin/subutai", "list", "-t", self.module.params['name']], stdout=subprocess.PIPE).stdout.read()
        if self.module.params['name'] in output:
            return True
        else:
            return False

    def _is_demoted(self):
        output = subprocess.Popen(
            ["/snap/bin/subutai", "list", "-c", self.module.params['name']], stdout=subprocess.PIPE).stdout.read()
        if self.module.params['name'] in output:
            return True
        else:
            return False

    def _subutai_cmd(self, cmd):
        err_msg = subprocess.Popen(
            ["/snap/bin/subutai", cmd, self.module.params['name']] + self.args, stderr=subprocess.PIPE).stderr.read()
        return err_msg

def main():
    Container()

if __name__ == '__main__':
    main()
