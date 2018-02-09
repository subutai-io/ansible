# ansible
Plugins and Drivers for Subutai Integration
===========================================


How to run: 
-----------

Inside this module directory, run: 

`ansible-playbook --module-path . test_module.yml -i ./hosts`

You'll need create a `hosts` file describing which servers this script will run, for example to run on localhost on port 2222: 

`localhost:2222`

To generate Markdown documentation run:

`./docgen.py`