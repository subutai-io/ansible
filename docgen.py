#!/usr/bin/env python

import importlib
import glob
import os
import yaml
from jinja2 import Template

class Module():
    def __init__(self):
        pass

    def gen_markdown(self, module):
        mod = importlib.import_module(module)
        dict_doc = self.digest_documentation(mod.DOCUMENTATION)
        template = Template(open("templates/ansible-docs.j2").read())
        dict_doc['examples'] = mod.EXAMPLES

        if not os.path.exists("docs"):
            os.mkdir("docs")

        fd = open("docs/{}.md".format(module), "w")
        fd.write(template.render(modules=dict_doc))
        fd.close()

    def digest_documentation(self, doc):
        """
        >>> DOCUMENTATION = '''
        ...             ---
        ...             module: subutai_vxlan
        ... 
        ...             short_description: subutai vxlan module
        ... 
        ...             version_added: "2.5"
        ... 
        ...             description:
        ...                 - "configure vxlan tunnels"
        ... 
        ...             options:
        ...                 command:
        ...                     description:
        ...                         - create, delete
        ...                     required: true
        ...                 name:
        ...                     description:
        ...                         - tunnel name
        ...                     required: false
        ...                 remoteip:
        ...                     description:
        ...                         - remote IP address
        ...                     required: false
        ...                 vlan:
        ...                     description:
        ...                         - vlan name
        ...                     required: false
        ...                 vni:
        ...                     description:
        ...                         - VXLAN tunnel VNI
        ...                     required: false
        ...         '''
        >>> m = Module()
        >>> m.digest_documentation(DOCUMENTATION)
        {'module': 'subutai_vxlan', 'short_description': 'subutai vxlan module', 'version_added': '2.5', 'description': ['configure vxlan tunnels'], 'options': {'command': {'description': ['create, delete'], 'required': True}, 'name': {'description': ['tunnel name'], 'required': False}, 'remoteip': {'description': ['remote IP address'], 'required': False}, 'vlan': {'description': ['vlan name'], 'required': False}, 'vni': {'description': ['VXLAN tunnel VNI'], 'required': False}}}
        """

        doc = doc.replace("---", "")
        return yaml.load(doc)

if __name__ == '__main__':
    m = Module()
    for mod in glob.glob("subutai_*py"):
        m.gen_markdown(mod.replace(".py",""))
        print("{}...".format(mod))