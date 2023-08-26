#!/usr/bin/python
#
# Copyright 2019 Craig Spry
#
# weewx driver that reads data from a MQTT
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.
#
# See http://www.gnu.org/licenses/

from __future__ import with_statement
import json
import logging
import time
from queue import Queue
from threading import Thread

import paho.mqtt.client as paho

import weewx.drivers

DRIVER_NAME = 'DodgyMQTT'
DRIVER_VERSION = "0.001"

log = logging.getLogger(__name__)


def _get_as_float(d):
    v = None
    try:
        v = float(d)
    except ValueError as e:
        log.error("cannot read value for '%s': %s" % (d, e))
    return v


def on_message(client, userdata, message):
    data = json.loads(message.payload.decode("utf-8"))
    userdata['message_q'].put(data)


def mqtt_reader(out_q):
    print("listner started")
    client_data = {'message_q': out_q}
    client = paho.Client("weewx_client", userdata=client_data)
    client.connect('localhost', 1883)
    client.on_message = on_message
    client.subscribe("weather/all")
    client.loop_start()


def loader(config_dict, engine):
    q = Queue()
    driver = DodgyMQTT(q)
    t1 = Thread(target=mqtt_reader, args=(q,))
    t1.start()
    return driver


class DodgyMQTT(weewx.drivers.AbstractDevice):
    """weewx driver that reads data from a file"""
    def __init__(self, in_q):
        # where to find the data file
        self.in_q = in_q

    def genLoopPackets(self):
        while True:
            # read whatever values we can get from the file
            data = {}
            try:
                data = self.in_q.get()
            except Exception as e:
                log.error("read failed: %s" % e)
            # map the data into a weewx loop packet
            _packet = {'dateTime': int(time.time() + 0.5),
                       'usUnits': weewx.METRICWX,
                       'outTemp': _get_as_float(data['temperature']),
                       'pressure': _get_as_float(data['pressure']) / 100.0,
                       'rain': _get_as_float(data['rainfall']),
                       'windSpeed': _get_as_float(data['windspeed']),
                       'windDir': int(data['winddir']),
                       'cloudbase': _get_as_float(data['cloudheight']),
                       'outHumidity': _get_as_float(data['humidity'])}
            yield _packet

    @property
    def hardware_name(self):
        return "DodgyMQTT"


# To test this driver, run it directly as follows:
#   PYTHONPATH=/home/weewx/bin python /home/weewx/bin/user/dodgy_mqtt.py
if __name__ == "__main__":
    import weeutil.weeutil
    import weeutil.logger
    import weewx
    weewx.debug = 1
    weeutil.logger.setup('dodgy_mqtt', {})
    q = Queue()
    print("starting")
    driver = DodgyMQTT(q)
    t1 = Thread(target=mqtt_reader, args=(q,))
    t1.start()
    for packet in driver.genLoopPackets():
        print(weeutil.weeutil.timestamp_to_string(packet['dateTime']), packet)
