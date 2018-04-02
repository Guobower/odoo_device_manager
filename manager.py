#!/usr/bin/env python3
#import aiojobs
#import aiofiles
#import aiohttp
import asyncio
from hbmqtt.mqtt.constants import QOS_2
#import aiodocker
#from aiodocker.exceptions import DockerError
#from datetime import datetime, timezone
import json
import logging
import os
#import secrets
#import string
#import time
#import sys
#import yaml
#from aiodocker import Docker
from mqttrpc import MQTTRPC, OdooRPCProxy, dispatcher
from tinyrpc.exc import RPCError

logger = logging.getLogger(__name__)
#logging.getLogger('aiohttp-json-rpc.client').setLevel(level=logging.DEBUG)

ODOO_DB = os.environ.get('ODOO_DB', 'test')
ODOO_USER = 'admin'
ODOO_PASSWORD = 'admin'
# Every seconds lookup logs and send to the cloud
UPDATE_DEVICES_INTERVAL = int(os.environ.get('LOG_INTERVAL', '120'))

class Manager(MQTTRPC):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.odoo = OdooRPCProxy(self, 'odoo')


    async def start(self):
        self.loop.create_task(self.process_messages())
        # Init odoo connector
        try:
            uid = await self.odoo.login(ODOO_DB, ODOO_USER, ODOO_PASSWORD)
        except RPCError as e:
            raise
        # Subscribe for will messages
        await self.subscribe([('will/+', QOS_2)])


    async def on_message(self, message):
        if message.topic.startswith('will/'):
            print('Message: ', message.topic)
            uid = message.topic.split('/')[1]
            device_id = await self.odoo.search(
                                'device_manager.device', [('uid','=', uid)])
            if device_id:
                device_id = device_id[0]
                logger.info('Setting device UID {} ID {} offline'.format(
                                                            uid, device_id))
                await self.odoo.write('device_manager.device', device_id, 
                                                        {'state': 'offline'})
        else:
            logger.info('Unknown topic')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('hbmqtt').setLevel(level=logging.ERROR)
    loop = asyncio.get_event_loop()
    m = Manager(loop=loop)
    loop.create_task(m.start())
    try:
        loop.run_forever()
    finally:
        logger.info('Stopped')

