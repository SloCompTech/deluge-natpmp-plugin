# -*- coding: utf-8 -*-
# Copyright (C) 2024 Martin Dagarin <martin.dagarin@gmail.com>
#
# Basic plugin template created by the Deluge Team.
#
# This file is part of natpmp and is licensed under GNU GPL 3.0, or later,
# with the additional special exception to link portions of this program with
# the OpenSSL library. See LICENSE for more details.
from __future__ import unicode_literals

from datetime import datetime
import logging
import os
import re
import shlex
from subprocess import check_output, CalledProcessError, STDOUT, TimeoutExpired

import deluge.component as component
import deluge.configmanager
from deluge.core.rpcserver import export
from deluge.plugins.pluginbase import CorePluginBase
from twisted.internet.task import LoopingCall

log = logging.getLogger(__name__)

DEFAULT_PREFS = {
    'enabled': False,
    'exec_path': 'natpmpc',
    'timeout': 2,
    'gateway_address': '10.2.0.1',
    'preffered_public_port': 1,
    'preffered_private_port': 0,
    'refresh_interval': 45,
    'lifetime_interval': 60,
    'portchange_command': '',
}

def parse_natpmpc_response(str):
  response = {}

  match_gateway = re.search(r'\busing gateway : ([0-9a-fA-F\.\:]+)\b', str)
  response['gateway'] = match_gateway.groups()[0] if match_gateway is not None else None

  match_publicip = re.search(r'\bPublic IP address : ([0-9a-fA-F\.\:]+)\b', str)
  response['public_ip'] = match_publicip.groups()[0] if match_publicip is not None else None

  match_port = re.search(r'\bMapped public port (\d{1,5}) protocol (\w{3}) to local port (\d{1,5}) lifetime (\d+)\b', str)
  response['proto'] = match_port.groups()[1] if match_port is not None else None
  response['public_port'] = int(match_port.groups()[0]) if match_port is not None else None
  response['private_port'] = int(match_port.groups()[2]) if match_port is not None else None

  return response

class Core(CorePluginBase):
    def enable(self):
        self.config = deluge.configmanager.ConfigManager('natpmp.conf', DEFAULT_PREFS)
        self.refresh_timer = LoopingCall(self.refresh)
        self.last_update = ''
        self.public_ip_address = ''
        self.current_port = ''

    def disable(self):
        self.stop_refresh_timer()
        self.last_update = ''
        self.public_ip_address = ''
        self.current_port = ''

    def update(self):
        if self.config['enabled']:
            self.start_refresh_timer()
        else:
            self.stop_refresh_timer()

    def start_refresh_timer(self):
        if not self.refresh_timer or self.refresh_timer.running or not self.config['enabled']:
            return
        if not self.is_command_valid(self.config['exec_path']):
            return
        log.debug(f'Starting refresh timer with interval {self.config["refresh_interval"]}s')
        self.refresh_timer.start(self.config['refresh_interval'])
    
    def stop_refresh_timer(self):
        if not self.refresh_timer or not self.refresh_timer.running:
            return
        log.debug('Stopping refresh timer')
        self.refresh_timer.stop()

    def refresh(self):
        # Refresh UDP port
        data_udp = None
        output_udp = None
        try:
            command = shlex.split(f'{self.config["exec_path"]} -a {shlex.quote(str(self.config["preffered_public_port"]))} {shlex.quote(str(self.config["preffered_private_port"]))} udp {shlex.quote(str(self.config["lifetime_interval"]))} -g {shlex.quote(self.config["gateway_address"])}')
            output_udp = check_output(command, stderr=STDOUT, timeout=(self.config['timeout'] if self.config['timeout'] > 0 else None)).decode()
            data_udp = parse_natpmpc_response(output_udp)
        except CalledProcessError as e:
            output_udp = e.stdout.decode()
            log.warning('Refresh UDP port: error')
            log.warning(output_udp)
        except TimeoutExpired as e:
            output_udp = e.stdout.decode()
            log.warning('Refresh UDP port timedout')

        # Refresh TCP port
        data_tcp = None
        output_tcp = None
        try:
            command = shlex.split(f'{self.config["exec_path"]} -a {shlex.quote(str(self.config["preffered_public_port"]))} {shlex.quote(str(self.config["preffered_private_port"]))} tcp {shlex.quote(str(self.config["lifetime_interval"]))} -g {shlex.quote(self.config["gateway_address"])}')
            output_tcp = check_output(command, stderr=STDOUT, timeout=(self.config['timeout'] if self.config['timeout'] > 0 else None)).decode()
            data_tcp = parse_natpmpc_response(output_tcp)
        except CalledProcessError as e:
            output_tcp = e.stdout.decode()
            log.warning('Refresh TCP port: error')
            log.warning(output_tcp)
        except TimeoutExpired as e:
            output_tcp = e.stdout.decode()
            log.warning('Refresh TCP port timedout')

        if data_udp is not None and data_udp['proto'] is not None and data_tcp is not None and data_tcp['proto'] is not None:
            core = component.get("Core")
            current_port = core.get_listen_port()
            new_udp_port = data_udp['public_port']
            new_tcp_port = data_tcp['public_port']
            if current_port != new_tcp_port or current_port != new_udp_port:
                # Update info
                self.last_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.current_port = f'{new_udp_port} / {new_tcp_port}'
                self.public_ip_address = data_udp['public_ip']

                # Reconfiure listen ports
                core.set_config({"listen_ports": [new_udp_port, new_tcp_port]})
                log.info(f'Changed listening port from {current_port} to {new_udp_port},{new_tcp_port}')

                # Run port change script
                if self.is_command_valid(self.config['portchange_command']):
                    try:
                        log.debug('Port change command: run')
                        command = shlex.split(f'{self.config["portchange_command"]} {current_port} {new_udp_port} {new_tcp_port}')
                        output = check_output(command, stderr=STDOUT, timeout=(self.config['timeout'] if self.config['timeout'] > 0 else None)).decode()
                        log.debug('Port change command: done')
                    except CalledProcessError as e:
                        output = e.stdout.decode()
                        log.warning('Port change command: error')
                        log.warning(output)
                    except TimeoutExpired as e:
                        output = e.stdout.decode()
                        log.warning('Port change command: timed out')

                # Reannounce torrents
                log.info('Reannouncing torrents')
                torrents = core.get_session_state()
                core.force_reannounce(torrents)
                log.info('Torrents reannounced')

        else: # Error
            log.warning('Failed to update NAT-PMP mapped port')
            log.warning(output_udp)
            log.warning(output_tcp)

    #
    #   Checks if command is valid
    #
    @export
    def is_command_valid(self, str):
        str = str.strip() # Strip spaces
        if len(str) < 1:
            return False
        str_parts = str.split(' ')
        execstr = str_parts[0]
        if execstr.startswith('/') or execstr.startswith('.'): # Check if absolute or relative path is provided to program or script
            return os.path.exists(execstr) # OK if program/script exists
        # Check if command exists
        # TODO: Change execution based on OS
        res = os.system(f'which {execstr}')
        return res == 0

    @export
    def set_config(self, config):
        # Check if config has changed
        config_changed = False
        for key in config:
            if self.config[key] != config[key]:
                config_changed = True
                break
        
        if config_changed:
            self.stop_refresh_timer()

        for key in config:
            self.config[key] = config[key]
        self.config.save()

        if config_changed:
            self.start_refresh_timer()

    @export
    def get_config(self):
        return self.config.config
    
    @export
    def get_status(self):
        return {
            'last_update': self.last_update,
            'public_ip_address': self.public_ip_address,
            'current_port': self.current_port,
        }
