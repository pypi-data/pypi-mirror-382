#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Defaults and fallback configuration values.
"""
import os

#: fallback configuration key/value pairs
#: (to be overriden by environment variables)
ESMERALDA_CONFIG = dict(
    time_out_url='http://time:out@localhost:5984/time_out',
    run_reports_url='http://time:out@localhost:5984/run_reports',
    ansible_root_path=os.path.join(
        os.environ.get("HOME", ''), "ansible-playbooks"),
    ansible_playbook_binary="/usr/bin/ansible-playbook",
    amqp_port = 5672,
    dispatch_queue="esmeralda_request",
    inventory='etc/00-merged-dummy',
    playbook='information-dumping.yml',
    ansible_config='etc/ansible.cfg'
)

"""
+-------------------------------------------+---------------------------------+
| Environment Variable                      | Description                     |
+===========================================+=================================+
| ``ESMERALDA_TIME_OUT_URL``                | CouchDB URL for storing         |
|                                           | *time out* state                |
+-------------------------------------------+---------------------------------+
| ``ESMERALDA_RUN_REPORTS_URL``             | CouchDB URL for storing         |
|                                           | run reports                     |
+-------------------------------------------+---------------------------------+
| ``ESMERALDA_AMQP_PORT``                   | AMQP port override              |
+-------------------------------------------+---------------------------------+
| ``ESMERALDA_DISPATCH_QUEUE``              | Message queue to which          |
|                                           | dispatched request will be      |
|                                           | published                       |
+-------------------------------------------+---------------------------------+
| ``ESMERALDA_ANSIBLE_CONFIG``              | (relative) Path of ansible      |
|                                           | configuration file              |
+-------------------------------------------+---------------------------------+
| ``ESMERALDA_ANSIBLE_ROOT_PATH``           | Path of playbooks and roles     |
+-------------------------------------------+---------------------------------+
| ``ESMERALDA_ANSIBLE_PLAYBOOK_BINARY``     | Path of ansible-playbook script |
+-------------------------------------------+---------------------------------+
| ``ESMERALDA_INVENTORY``                   | (relative) Path of inventory    |
|                                           | file                            |
+-------------------------------------------+---------------------------------+
| ``ESMERALDA_PLAYBOOK``                    | (relative) Path of playbook     |
|                                           | file                            |
+-------------------------------------------+---------------------------------+

"""

PREFIX = 'ESMERALDA_'

for key in ESMERALDA_CONFIG:
    env_key = PREFIX + key.upper()

    try:
        ESMERALDA_CONFIG[key] = os.environ[env_key]
    except KeyError:
        pass
