Plugins and Drivers for Subutai Integration
===========================================

How to run
-----------

Inside this module directory, run: 

`ansible-playbook --module-path . tests/all_tests.yml -i ./hosts`

Replace `tests/all_tests.yml` with path to your recipe/playbook.

You'll need create a `hosts` file describing which servers this script will run, for example to run on localhost on port 2222: 

`localhost:2222`

Unmerged modules
----------------

This branch have script from early version of this module, but ansible upstream developers advise us to merge all scripts in one single file, and only with essential functions to be validade by the community. Because that not all functionality is present in on `subutai.py` module. The original modules stay on `unmerged` directory  and they are outdated (designed for subutai 6.x).

Generating Documentation
------------------------ 

To generate Markdown documentation run:

`./docgen.py`

Online documentation for subutai module can be found in: https://github.com/subutai-io/ansible/wiki/subutai
