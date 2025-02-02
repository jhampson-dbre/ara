ARA Records Ansible
===================

ARA Records Ansible and makes it easier to understand and troubleshoot.

It's another recursive acronym.

.. image:: doc/source/_static/ara-with-icon.png

What it does
============

Simple to install and get started, ara provides reporting by saving detailed and granular results of ``ansible`` and ``ansible-playbook`` commands wherever you run them:

- by hand or from a script
- from a laptop, a desktop, a container or a server
- for development, CI or production
- from a linux distribution or even on OS X (as long as you have ``python >= 3.5``)
- from tools such as AWX or Tower, Jenkins, GitLab CI, Rundeck, Zuul, Molecule, ansible-pull, ansible-test or ansible-runner

By default, ara's Ansible callback plugin will record data to a local sqlite database without requiring you to run a server or a service:

.. image:: doc/source/_static/ara-quickstart-default.gif

ara can also provide a single pane of glass when recording data from multiple locations by pointing the callback plugin to a running API server:

.. image:: doc/source/_static/ara-quickstart-server.gif

The data is then made available for browsing, searching and querying over the included reporting interface, a CLI client as well as a REST API.

How it works
============

ARA Records Ansible execution results to sqlite, mysql or postgresql databases by
using an `Ansible callback plugin <https://docs.ansible.com/ansible/latest/plugins/callback.html>`_.

This callback plugin leverages built-in python API clients to send data to a REST API server:

.. image:: doc/source/_static/graphs/recording-workflow.png

What it looks like
==================

API browser
-----------

Included by the API server with django-rest-framework, the API browser allows
users to navigate the different API endpoints and query recorded data.

.. image:: doc/source/_static/ui-api-browser.gif

Reporting interface
-------------------

A simple reporting interface built-in to the API server without any extra
dependencies.

.. image:: doc/source/_static/ui-reporting.gif

ara CLI
-------

A built-in CLI client for querying and managing playbooks and their recorded data.

.. image:: doc/source/_static/cli-playbook-list.png

The full list of commands, their arguments as well as examples can be found in
the `CLI documentation <https://ara.readthedocs.io/en/latest/cli.html#cli-ara-api-client>`_.

Getting started
===============

Requirements
------------

- Any recent Linux distribution or Mac OS with python >=3.5 available
- The ara Ansible plugins must be installed for the same python interpreter as Ansible itself

For RHEL 7 and CentOS 7 it is recommended to run the API server in a container due to missing or outdated dependencies.
See this `issue <https://github.com/ansible-community/ara/issues/99>`_ for more information.

Recording playbooks without an API server
-----------------------------------------

With defaults and using a local sqlite database:

.. code-block:: bash

    # Install Ansible and ARA (with API server dependencies) for the current user
    python3 -m pip install --user ansible "ara[server]"

    # Configure Ansible to use the ARA callback plugin
    export ANSIBLE_CALLBACK_PLUGINS="$(python3 -m ara.setup.callback_plugins)"

    # Run an Ansible playbook
    ansible-playbook playbook.yaml

    # Use the CLI to see recorded playbooks
    ara playbook list

    # Start the built-in development server to browse recorded results
    ara-manage runserver

Recording playbooks with an API server
--------------------------------------

You can get an API server deployed using the `ara Ansible collection <https://github.com/ansible-community/ara-collection>`_
or get started quickly using the container images from `DockerHub <https://hub.docker.com/r/recordsansible/ara-api>`_ and
`quay.io <https://quay.io/repository/recordsansible/ara-api>`_:

.. code-block:: bash

    # Create a directory for a volume to store settings and a sqlite database
    mkdir -p ~/.ara/server

    # Start an API server with podman from the image on DockerHub:
    podman run --name api-server --detach --tty \
      --volume ~/.ara/server:/opt/ara:z -p 8000:8000 \
      docker.io/recordsansible/ara-api:latest

    # or with docker from the image on quay.io:
    docker run --name api-server --detach --tty \
      --volume ~/.ara/server:/opt/ara:z -p 8000:8000 \
      quay.io/recordsansible/ara-api:latest

Once the server is running, ara's Ansible callback plugin must be installed and configured to send data to it:

.. code-block:: bash

    # Install Ansible and ARA (without API server dependencies) for the current user
    python3 -m pip install --user ansible ara

    # Configure Ansible to use the ARA callback plugin
    export ANSIBLE_CALLBACK_PLUGINS="$(python3 -m ara.setup.callback_plugins)"

    # Set up the ARA callback to know where the API server is located
    export ARA_API_CLIENT="http"
    export ARA_API_SERVER="http://127.0.0.1:8000"

    # Run an Ansible playbook
    ansible-playbook playbook.yaml

    # Use the CLI to see recorded playbooks
    ara playbook list

Data will be available on the API server in real time as the playbook progresses and completes.

You can read more about how container images are built and how to run them in the `documentation <https://ara.readthedocs.io/en/latest/container-images.html>`_.

Live demo
=========

A live demo is deployed with the ara Ansible collection from `Ansible galaxy <https://galaxy.ansible.com/recordsansible/ara>`_.

It is available at https://demo.recordsansible.org.

Documentation
=============

Documentation for installing, configuring, running and using ARA is
available on `readthedocs.io <https://ara.readthedocs.io>`_.

Community and getting help
==========================

- Bugs, issues and enhancements: https://github.com/ansible-community/ara/issues
- IRC: #ara on `Freenode <https://webchat.freenode.net/?channels=#ara>`_
- Slack: https://arecordsansible.slack.com (`invitation link <https://join.slack.com/t/arecordsansible/shared_invite/enQtMjMxNzI4ODAxMDQxLTU2NTU3YjMwYzRlYmRkZTVjZTFiOWIxNjE5NGRhMDQ3ZTgzZmQyZTY2NzY5YmZmNDA5ZWY4YTY1Y2Y1ODBmNzc>`_)

- Website and blog: https://ara.recordsansible.org
- Twitter: https://twitter.com/recordsansible

Contributing
============

Contributions to the project are welcome and appreciated !

Get started with the `contributor's documentation <https://ara.readthedocs.io/en/latest/contributing.html>`_.

Authors
=======

Contributors to the project can be viewed on
`GitHub <https://github.com/ansible-community/ara/graphs/contributors>`_.

Copyright
=========

::

    Copyright (c) 2021 The ARA Records Ansible authors

    ARA Records Ansible is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    ARA Records Ansible is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with ARA Records Ansible.  If not, see <http://www.gnu.org/licenses/>.
