# -*- coding: utf-8 -*-
# Copyright (C) 2024 Martin Dagarin <martin.dagarin@gmail.com>
#
# Basic plugin template created by the Deluge Team.
#
# This file is part of natpmp and is licensed under GNU GPL 3.0, or later,
# with the additional special exception to link portions of this program with
# the OpenSSL library. See LICENSE for more details.
from __future__ import unicode_literals

import logging

from gi.repository import Gtk

import deluge.component as component
from deluge.plugins.pluginbase import Gtk3PluginBase
from deluge.ui.client import client

from .common import get_resource

log = logging.getLogger(__name__)


class Gtk3UI(Gtk3PluginBase):
    def enable(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(get_resource('config.ui'))

        self.builder.connect_signals({
            # TODO: Configure hooks to get exec_path and port_change_path
        })

        component.get('Preferences').add_page(
            'NAT-PMP', self.builder.get_object('natpmp_box'))
        component.get('PluginManager').register_hook(
            'on_apply_prefs', self.on_apply_prefs)
        component.get('PluginManager').register_hook(
            'on_show_prefs', self.on_show_prefs)

    def disable(self):
        component.get('Preferences').remove_page('NAT-PMP')
        component.get('PluginManager').deregister_hook(
            'on_apply_prefs', self.on_apply_prefs)
        component.get('PluginManager').deregister_hook(
            'on_show_prefs', self.on_show_prefs)

    def on_apply_prefs(self):
        log.debug('applying prefs for natpmp')
        config = {
            'enabled': self.builder.get_object('natpmp_enabled_checkbutton').get_active(),
            'exec_path': self.builder.get_object('natpmp_executable_path_entry').get_text(),
            'timeout': self.builder.get_object('natpmp_executable_timeout_spinbutton').get_value_as_int(),
            'gateway_address': self.builder.get_object('natpmp_executable_gateway_address_entry').get_text(),
            'preffered_public_port': self.builder.get_object('natpmp_executable_preffered_public_port_spinbutton').get_value_as_int(),
            'preffered_private_port': self.builder.get_object('natpmp_executable_preffered_private_port_spinbutton').get_value_as_int(),
            'refresh_interval': self.builder.get_object('natpmp_executable_refresh_interval_spinbutton').get_value_as_int(),
            'lifetime_interval': self.builder.get_object('natpmp_executable_lifetime_interval_spinbutton').get_value_as_int(),
            'portchange_command': self.builder.get_object('natpmp_commands_portchange_entry').get_text(),
        }
        client.natpmp.set_config(config)

    def on_show_prefs(self):
        client.natpmp.get_config().addCallback(self.cb_get_config)
        client.natpmp.get_status().addCallback(self.cb_get_status)

    def cb_get_config(self, config):
        self.builder.get_object('natpmp_enabled_checkbutton').set_active(config['enabled'])
        self.builder.get_object('natpmp_executable_path_entry').set_text(config['exec_path'])
        self.builder.get_object('natpmp_executable_timeout_spinbutton').set_value(config['timeout']),
        # TODO: Check if exec_path is invalid
        self.builder.get_object('natpmp_executable_gateway_address_entry').set_text(config['gateway_address']),
        self.builder.get_object('natpmp_executable_preffered_public_port_spinbutton').set_value(config['preffered_public_port']),
        self.builder.get_object('natpmp_executable_preffered_private_port_spinbutton').set_value(config['preffered_private_port']),
        self.builder.get_object('natpmp_executable_refresh_interval_pinbutton').set_value(config['refresh_interval'])
        self.builder.get_object('natpmp_executable_lifetime_interval_pinbutton').set_value(config['lifetime_interval'])
        self.builder.get_object('natpmp_commands_portchange_entry').set_text(config['portchange_command'])
        # TODO: Check if portchange_command is invalid
    
    def cb_get_status(self, status):
        self.builder.get_object('natpmp_status_lastupdate_value_label').set_label(status['last_update'])
        self.builder.get_object('natpmp_status_public_ip_value_label').set_label(status['public_ip_address'])
        self.builder.get_object('natpmp_status_currentport_value_label').set_label(status['current_port'])
