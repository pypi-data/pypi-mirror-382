#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Controller classes and helper functions for message queue based running of
(ansible) tasks.
"""
import os
import logging
import subprocess
from subprocess import PIPE
import json
from tempfile import NamedTemporaryFile
import uuid

import pendulum
from djali.couchdb import CloudiControl
from quasimodo.amqp import QueueWorkerSkeleton
from jinja2 import Environment, BaseLoader

from esmeralda.defaults import ESMERALDA_CONFIG

#: default *time out* duration
TIME_OUT_DEFAULT = pendulum.Duration(hours=1)

#: single host inventory file template
INVENTORY_TEMPLATE = """[{{ group_name }}]
{{ inventory_hostname }}
"""


def setup_ansible_environment(**kwargs):
    """
    Set ansible environment variables for running a playbook.
    Values for omitted keyword arguments will fall back to their corresponding
    :py:data:`esmeralda.defaults.ESMERALDA_CONFIG` key/value pair.

    Keyword Args:
        ansible_root_path(str, optional): Path of playbooks and roles
        ansible_config_path(str, optional): (relative) Path of ansible configuration file
    """
    ansible_root_path = kwargs.get(
        "ansible_root_path", ESMERALDA_CONFIG['ansible_root_path'])
    ansible_config_path = kwargs.get(
        "ansible_config_path",
        os.path.join(ansible_root_path, ESMERALDA_CONFIG['ansible_config']))

    os.environ['ANSIBLE_CONFIG'] = ansible_config_path
    os.environ['ANSIBLE_STDOUT_CALLBACK'] = 'json'

    if kwargs.get("do_debug"):
        os.environ['ANSIBLE_LOG_PATH'] = '/tmp/esmeralda_ansible_debug.log'
        os.environ['ANSIBLE_DEBUG'] = 'True'



class TimeOutController(object):
    """
    Controller for managing *time outs* of items. An item can be marked as
    *in time out* - it is up to the caller to e.g. refuse taking actions based
    on the fact that an item is currently in time out.

    Attributes:
        log (logging.Logger): logger instance
        cc (djali.couchdb.CloudiControl): persistence layer controller instance

    Keyword Args:
        db_url (str, optional): CouchDB URL
    """
    def __init__(self, *args, **kwargs):
        self.log = logging.getLogger(__name__)
        db_url = kwargs.get("db_url", ESMERALDA_CONFIG['time_out_url'])
        self.cc = CloudiControl(db_url)

    def set_timeout(self, key, time_out=None):
        """
        Mark an item (e.g. a hostname) as *in time out*.

        Args:
            key (str): item/hostname identifier
            time_out (datetime.timedelta, optional):

        Returns:
            datetime.datetime: end of timeout
        """
        if time_out is None:
            time_out = TIME_OUT_DEFAULT

        u_now = pendulum.now(tz=pendulum.UTC)
        blocked_until = u_now + time_out
        doc = {
            'time_out': blocked_until.to_iso8601_string()
        }
        self.cc[key] = doc
        self.log.info("{key} will be in time out until {time_out}".format(
            key=key, **doc))

        return blocked_until

    def in_timeout(self, key):
        """
        Check if an item (e.g. a hostname) is currently ìn *time out*.

        Args:
            key (str): item/hostname identifier

        Returns:
            bool: ``True`` if item is considered *in time out*.
        """
        try:
            doc = self.cc[key]
        except KeyError:
            self.log.info("{key} is not in time out".format(key=key))
            return False

        blocked_until = pendulum.parse(doc['time_out'])
        u_now = pendulum.now(tz=pendulum.UTC)

        self.log.info(
            "{key} is supposed to be in time out until {time_out}".format(
                key=key, **doc))

        return u_now < blocked_until

    def clear_timeout(self, key):
        """
        Stop *time out* of an item (e.g. a hostname).

        Args:
            key (str): item/hostname identifier
        """
        try:
            del self.cc[key]
        except KeyError:
            self.log.info("{key} was not in time out".format(key=key))


class Dispatcher(QueueWorkerSkeleton):
    """
    Controller for dispatching ansible run requests on a per hostname basis.
    Honours hosts being in *time out*. If a host is marked as *in time out* no
    new ansible run request will be dispatched.
    """
    def __init__(self, *args, **kwargs):
        amqp_port = kwargs.get("amqp_port", ESMERALDA_CONFIG['amqp_port'])

        super().__init__(
            self,
            port=amqp_port,
            *args, **kwargs)

    def _handle_request(self, payload, **kwargs):
        """
        Message/request handling function.
        To be implemented by deriving classes.
        """
        try:
            inventory_hostname = payload['identity']['inventory_hostname']
        except KeyError:
            try:
                inventory_hostname = payload['inventory_hostname']
            except KeyError:
                self.log.error("Inventory hostname is mandatory!")
                return False

        identity = payload.get('identity')
        if identity is None:
            identity = dict(
                inventory_hostname=inventory_hostname,
                serial_number=uuid.uuid4().hex
            )

        toc = TimeOutController()
        in_time_out = toc.in_timeout(inventory_hostname)

        if in_time_out:
            self.log.info(
                "{inventory_hostname}/{serial_number} is in time out.".format(
                    **identity))
            return True

        toc.set_timeout(inventory_hostname)

        u_now = pendulum.now(pendulum.UTC)
        message_id = "{prefix}_{inventory_hostname}_{dt}".format(
            prefix="a",
            inventory_hostname=inventory_hostname,
            dt=u_now.format("YYYY-MM-DD_hhmmss")
        )
        self.log.info("Dispatching update request {:s} ... ".format(message_id))
        payload['message_id'] = message_id
        payload['dispatch_dt'] = u_now.to_iso8601_string()
        self.add_to_queue(payload, queue=ESMERALDA_CONFIG['dispatch_queue'])

        return True


class AnsibleExecutor(QueueWorkerSkeleton):
    """
    Controller for running ansible tasks posted to message queue.
    """
    def __init__(self, *args, **kwargs):
        amqp_port = kwargs.get("amqp_port", ESMERALDA_CONFIG['amqp_port'])

        try:
            self.verbose = int(kwargs.get("verbose"))
        except Exception:
            self.verbose = 0

        super().__init__(
            self,
            port=amqp_port,
            *args, **kwargs)


    def persist_report(self, message_id, report, **kwargs):
        db_url = kwargs.get("db_url", ESMERALDA_CONFIG['run_reports_url'])

        if not message_id:
            self.log.warning("No message ID, no reporting.")
            return False

        report['dt'] = pendulum.now(pendulum.UTC).to_iso8601_string()

        try:
            reporter = CloudiControl(db_url)
            reporter[message_id] = report
            return True
        except Exception as exc:
            self.log.error("Failed to persist report: {!s}".format(exc))

        return False

    def _handle_request(self, payload, **kwargs):
        """
        Message/request handling function.
        To be implemented by deriving classes.
        """
        wrap = AnsibleRunWrapper(verbose=self.verbose)
        run_args = dict()
        inventory_hostname = None
        message_id = payload.get("message_id")

        try:
            inventory_hostname = payload['identity']['inventory_hostname']
        except KeyError:
            try:
                inventory_hostname = payload['inventory_hostname']
            except KeyError:
                pass

        if inventory_hostname:
            run_args['inventory_hostname'] = inventory_hostname

        for override in ('playbook_path', 'inventory_path'):
            if payload.get(override):
                run_args[override] = payload[override]

        self.log.info("Ansible run {!r}".format(message_id))

        a_run_result = wrap.run(**run_args)

        report = dict(
            ansible_rc=None,
            ansible_result=None,
            ansible_run_args=run_args,
        )

        if a_run_result is not False:
            rc, result = a_run_result
            report['ansible_rc'] = rc
            report['ansible_result'] = result
            self.log.info("RC={!r}".format(rc))

            try:
                self.log.info("STATS:")
                self.log.info(result.get("stats"))
            except Exception as exc:
                self.log.warning(
                    "Running with {!r} did not provide "
                    "status information! ({!s})".format(run_args, exc))

            self.persist_report(message_id, report)

            return True
        else:
            self.log.warning(
                "Running with {!r} failed miserably ...".format(run_args))

        self.persist_report(message_id, report)

        return False


class AnsibleRunWrapper(object):
    """
    Controller for running ansible playbook.
    """

    def __init__(self, *args, **kwargs):
        self.log = logging.getLogger(__name__)
        self.ansible_root_path = kwargs.get(
            "ansible_root_path", ESMERALDA_CONFIG['ansible_root_path'])
        self.ansible_config_path = kwargs.get(
            "ansible_config_path",
            os.path.join(
                self.ansible_root_path, ESMERALDA_CONFIG['ansible_config'])
        )

        try:
            self.verbose = int(kwargs.get("verbose"))
        except Exception:
            self.verbose = 0

    def _run(self, **kwargs):
        os.chdir(self.ansible_root_path)

        playbook_path = kwargs.get(
            "playbook_path",
            os.path.join(self.ansible_root_path, ESMERALDA_CONFIG['playbook'])
        )

        inventory_path = kwargs.get(
            "inventory_path",
            os.path.join(self.ansible_root_path, ESMERALDA_CONFIG['inventory'])
        )

        self.log.debug(
            "Playbook {playbook_path}, inventory {inventory_path}".format(
                playbook_path=playbook_path, inventory_path=inventory_path))

        if not os.path.exists(os.path.abspath(self.ansible_root_path)):
            self.log.warning("Ansible root {p!r} does not exist!".format(
                p=self.ansible_root_path))

        if not os.path.exists(os.path.abspath(self.ansible_config_path)):
            self.log.warning(
                "Ansible configuration file {p!r} does not exist!".format(
                    p=self.ansible_config_path))

        if not os.path.exists(os.path.abspath(playbook_path)):
            self.log.warning(
                "Playbook file {p!r} does not exist!".format(p=playbook_path))

        if not os.path.exists(os.path.abspath(inventory_path)):
            self.log.warning(
                "Inventory file {p!r} does not exist!".format(
                    p=inventory_path))

        setup_ansible_environment(ansible_root_path=self.ansible_root_path,
                                  ansible_config_path=self.ansible_config_path)
        call_args = [
            ESMERALDA_CONFIG['ansible_playbook_binary'],
            '-i',
            inventory_path,
            playbook_path
        ]

        if self.verbose:
            self.log.info("Trying to run {!r}".format(call_args))

        proc = subprocess.run(call_args, stdout=PIPE, stderr=PIPE,
                              cwd=self.ansible_root_path)

        rc = proc.returncode
        result = None

        try:
            result = json.loads(proc.stdout)
        except Exception as exc:
            self.log.error("Failed to parse STDOUT: {!s}".format(exc))
            try:
                for x in proc.stdout.decode('utf-8').split("\n"):
                    self.log.error(x)
            except Exception as exc2:
                self.log.error(exc2)

        if self.verbose:
            self.log.info("RC={!r}".format(rc))

            if self.verbose >= 10 and result is not None:
                for line in json.dumps(result, indent=2).split("\n"):
                    self.log.info(line)

        return rc, result

    def generate_inventory(self, inventory_hostname):
        """
        Generate an ansible inventory file for given hostname.

        Args:
            inventory_hostname: hostname or IP address

        Returns:
            str: inventory file path
        """
        self.log.debug(
            "Generating inventory file for {!r}".format(inventory_hostname))

        inventory_template = Environment(
            loader=BaseLoader).from_string(INVENTORY_TEMPLATE)

        rendered_inventory = inventory_template.render({
            'inventory_hostname': inventory_hostname,
            'group_name': 'victims'
        })

        # Create a temporary file and write the template string to it
        hosts = NamedTemporaryFile(delete=False)
        hosts.write(rendered_inventory.encode('utf-8'))
        hosts.close()

        self.log.debug(
            "Generated inventory file for {!s}: {!s}".format(
                inventory_hostname, hosts.name))

        return hosts.name

    def run(self, **kwargs):
        """
        Run an ansible playbook with given parameters.

        Keyword Args:
            inventory_hostname (str, optional): target (host or IP address)
            playbook_path (str, optional): playbook override
            inventory_path (str, optional): inventory override

        Returns:
            tuple: return code and parsed STDOUT or ``False`` on severe error
        """
        if kwargs.get("inventory_hostname"):
            try:
                kwargs['inventory_path'] = self.generate_inventory(
                    kwargs.get("inventory_hostname"))
            except Exception as exc:
                self.log.error(
                    "Failed to generate inventory file: {!s}".format(exc))

                return False

            self.log.debug("Inventory hostname: {!r}".format(
                kwargs.get("inventory_hostname")))
        else:
            self.log.debug("No inventory hostname given ...")

        try:
            return self._run(**kwargs)
        except Exception as exc:
            self.log.error("Failed to run: {!s}".format(exc))

        return False
