/**
 * Script: natpmp.js
 *     The client-side javascript code for the natpmp plugin.
 *
 * Copyright:
 *     (C) Martin Dagarin 2024 <martin.dagarin@gmail.com>
 *
 *     This file is part of natpmp and is licensed under GNU GPL 3.0, or
 *     later, with the additional special exception to link portions of this
 *     program with the OpenSSL library. See LICENSE for more details.
 */
Ext.ns('Deluge.plugins.natpmp');

/**
 * @class Deluge.ux.preferences.natpmpPage
 * @extends Ext.Panel
 */
Deluge.plugins.natpmp.Page = Ext.extend(Ext.Panel, {
    title: _('NAT-PMP'),
    header: false,
    layout: 'fit',
    border: false,

    initComponent: function () {
        Deluge.plugins.natpmp.Page.superclass.initComponent.call(this);

        this.fieldset = new Ext.form.FieldSet({
            xtype: 'fieldset',
            border: false,
            title: _('NAT-PMP'),
            autoHeight: true,
            defaultType: 'textfield',
            style: 'margin-top: 3px; margin-bottom: 0px; padding-bottom: 0px;',
            width: '85%',
            labelWidth: 1,
        });

        this.chkEnabled = this.fieldset.add({
            fieldLabel: '',
            labelSeparator: '',
            name: 'natpmp_enable',
            xtype: 'checkbox',
            boxLabel: _('Enabled'),
            listeners: {
                check: function (object, checked) {
                    //this.setSmtpDisabled(!checked);
                },
                scope: this,
            },
        });

        this.hBoxExecPath = this.fieldset.add({
            fieldLabel: '',
            labelSeparator: '',
            name: 'natpmp_exec_fieldset',
            xtype: 'container',
            layout: 'hbox',
            disabled: true,
            items: [
                {
                    xtype: 'label',
                    text: _('Path:'),
                    margins: '6 0 0 6',
                },
                {
                    xtype: 'textfield',
                    margins: '2 0 0 4',
                },
            ],
        });

        this.hBoxExecTimeout = this.fieldset.add({
            fieldLabel: '',
            labelSeparator: '',
            name: 'natpmp_exec_timeout_fieldset',
            xtype: 'container',
            layout: 'hbox',
            disabled: true,
            items: [
                {
                    xtype: 'label',
                    text: _('Timeout:'),
                    margins: '6 0 0 6',
                },
                {
                    xtype: 'spinnerfield',
                    margins: '2 0 0 34',
                    width: 64,
                    decimalPrecision: 0,
                    minValue: 0,
                    maxValue: 65535,
                },
            ],
        });

        this.hBoxGatewayAddress = this.fieldset.add({
            fieldLabel: '',
            labelSeparator: '',
            name: 'natpmp_exec_gateway_address_fieldset',
            xtype: 'container',
            layout: 'hbox',
            disabled: true,
            items: [
                {
                    xtype: 'label',
                    text: _('Gateway address:'),
                    margins: '6 0 0 6',
                },
                {
                    xtype: 'textfield',
                    margins: '2 0 0 4',
                },
            ],
        });

        this.hBoxPrefferedPublicPort = this.fieldset.add({
            fieldLabel: '',
            labelSeparator: '',
            name: 'natpmp_exec_preffered_public_port_fieldset',
            xtype: 'container',
            layout: 'hbox',
            disabled: true,
            items: [
                {
                    xtype: 'label',
                    text: _('Preffered public port:'),
                    margins: '6 0 0 6',
                },
                {
                    xtype: 'spinnerfield',
                    margins: '2 0 0 34',
                    width: 64,
                    decimalPrecision: 0,
                    minValue: 0,
                    maxValue: 65535,
                },
            ],
        });

        this.hBoxPrefferedPrivatePort = this.fieldset.add({
            fieldLabel: '',
            labelSeparator: '',
            name: 'natpmp_exec_preffered_private_port_fieldset',
            xtype: 'container',
            layout: 'hbox',
            disabled: true,
            items: [
                {
                    xtype: 'label',
                    text: _('Preffered private port:'),
                    margins: '6 0 0 6',
                },
                {
                    xtype: 'spinnerfield',
                    margins: '2 0 0 34',
                    width: 64,
                    decimalPrecision: 0,
                    minValue: 0,
                    maxValue: 65535,
                },
            ],
        });

        this.hBoxRefreshInterval = this.fieldset.add({
            fieldLabel: '',
            labelSeparator: '',
            name: 'natpmp_exec_refresh_interval_fieldset',
            xtype: 'container',
            layout: 'hbox',
            disabled: true,
            items: [
                {
                    xtype: 'label',
                    text: _('Refresh interval'),
                    margins: '6 0 0 6',
                },
                {
                    xtype: 'spinnerfield',
                    margins: '2 0 0 34',
                    width: 64,
                    decimalPrecision: 0,
                    minValue: 0,
                    maxValue: 86400,
                },
                {
                    xtype: 'label',
                    text: _('s'),
                    margins: '6 0 0 6',
                },
            ],
        });

        this.hBoxLifetimeInterval = this.fieldset.add({
            fieldLabel: '',
            labelSeparator: '',
            name: 'natpmp_exec_lifetime_interval_fieldset',
            xtype: 'container',
            layout: 'hbox',
            disabled: true,
            items: [
                {
                    xtype: 'label',
                    text: _('Lifetime interval'),
                    margins: '6 0 0 6',
                },
                {
                    xtype: 'spinnerfield',
                    margins: '2 0 0 34',
                    width: 64,
                    decimalPrecision: 0,
                    minValue: 0,
                    maxValue: 86400,
                },
                {
                    xtype: 'label',
                    text: _('s'),
                    margins: '6 0 0 6',
                },
            ],
        });

        this.hBoxPortChangeCommand = this.fieldset.add({
            fieldLabel: '',
            labelSeparator: '',
            name: 'natpmp_exec_port_change_command_fieldset',
            xtype: 'container',
            layout: 'hbox',
            disabled: true,
            items: [
                {
                    xtype: 'label',
                    text: _('Port change:'),
                    margins: '6 0 0 6',
                },
                {
                    xtype: 'textfield',
                    margins: '2 0 0 4',
                },
            ],
        });

        this.on('show', this.updateConfig, this);
    },

    updateConfig: function () {
        deluge.client.natpmp.get_config({
            success: function (config) {
                this.chkEnabled.setValue(config['enabled']);
                this.hBoxExecPath.getComponent(1).setValue(config['exec_path']);
                this.hBoxExecTimeout.getComponent(1).setValue(config['timeout']);
                this.hBoxGatewayAddress.getComponent(1).setValue(config['gateway_address']);
                this.hBoxPrefferedPublicPort.getComponent(1).setValue(config['preffered_public_port']);
                this.hBoxPrefferedPrivatePort.getComponent(1).setValue(config['preffered_private_port']);
                this.hBoxRefreshInterval.getComponent(1).setValue(config['refresh_interval']);
                this.hBoxLifetimeInterval.getComponent(1).setValue(config['lifetime_interval']);
                this.hBoxPortChangeCommand.getComponent(1).setValue(config['portchange_command']);
            },
            scope: this,
        });
    },

    onApply: function () {
        var config = {};

        config['enabled'] = this.chkEnabled.getValue();
        config['exec_path'] = this.hBoxExecPath.getComponent(1).getValue();
        config['timeout'] = Number(this.hBoxExecTimeout.getComponent(1).getValue());
        config['gateway_address'] = this.hBoxGatewayAddress.getComponent(1).getValue();
        config['preffered_public_port'] = Number(this.hBoxPrefferedPublicPort.getComponent(1).getValue());
        config['preffered_private_port'] = Number(this.hBoxPrefferedPrivatePort.getComponent(1).getValue());
        config['refresh_interval'] = Number(this.hBoxRefreshInterval.getComponent(1).getValue());
        config['lifetime_interval'] = Number(this.hBoxLifetimeInterval.getComponent(1).getValue());
        config['portchange_command'] = this.hBoxPortChangeCommand.getValue();

        deluge.client.natpmp.set_config(config);
    },

    onOk: function () {
        this.onApply();
    },

    onDestroy: function () {
        deluge.preferences.un('show', this.updateConfig, this);

        Deluge.plugins.natpmp.Page.superclass.onDestroy.call(this);
    },
});

Deluge.plugins.natpmp.Plugin = Ext.extend(Deluge.Plugin, {
    name: 'NAT-PMP',
    
    onDisable: function() {
        deluge.preferences.removePage(this.prefsPage);
        this.prefsPage = null;
    },

    onEnable: function() {
        if (!this.prefsPage) {
            this.prefsPage = deluge.preferences.addPage(
                new Deluge.plugins.natpmp.Page()
            );
        }
    }
});
Deluge.registerPlugin('NAT-PMP', Deluge.plugins.natpmp.Plugin);
