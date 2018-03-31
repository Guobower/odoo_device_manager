# -*- coding: utf-8 -*-
import json
import logging
from odoo import http, fields
from odoo.exceptions import Warning
from werkzeug.exceptions import NotFound
import sys

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Container(http.Controller):
     @http.route('/device_manager/register', auth='public', type='json')
     def register(self):
        token = http.request.jsonrequest.get('token')
        uid = http.request.jsonrequest.get('uid')
        app = http.request.env['device_manager.application'].sudo().search(
                                            [('token','=', token)])
        if not app:
            raise Warning('Application token not found')
        # Now check if the device is already registered
        device = http.request.env['device_manager.device'].sudo().search(
            [('uid','=',uid)])
        if device:
            # Check application
            if device.application.id != app.id:
                logger.warning('Device {} already registered with app {}'.format(
                    uid, device.application.name))
                raise Warning('Device {} already registered to app {}'.format(
                    uid, device.application.name))
            else:
                device.last_online = fields.Datetime.now()
                logger.debug(
                    'Device {} is already registered'.format(uid))
        else:
            device = http.request.env['device_manager.device'].register(app,
                                                    http.request.jsonrequest)
        return {
            'mqtt_host': http.request.env['device_manager.settings']._get_param(
                                                                    'mqtt_host'),
            'mqtt_port': http.request.env['device_manager.settings']._get_param(
                                                                    'mqtt_port'),
            'device_id': device.id,
        }

