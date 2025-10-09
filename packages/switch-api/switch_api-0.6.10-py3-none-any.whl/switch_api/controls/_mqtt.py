# -------------------------------------------------------------------------
# Copyright (c) Switch Automation Pty Ltd. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
A module containing the SwitchMQTT class and associated methods referenced by the controls module in the package. This
module is not directly referenced by end users.
"""
import json
import logging
import sys
import time
from urllib.parse import urlparse
import paho.mqtt.client as mqtt
import pandas
from paho.mqtt.client import MQTTMessage
from ._constants import (CONTROL_REQUEST_ACTION_ACK, CONTROL_REQUEST_ACTION_RESULT, WS_DEFAULT_PORT,
                         WS_MQTT_CONNECTION_TIMEOUT, WS_MQTT_WAIT_TIME_INTERVAL)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
consoleHandler = logging.StreamHandler(stream=sys.stdout)
consoleHandler.setLevel(logging.INFO)

logger.addHandler(consoleHandler)
formatter = logging.Formatter('%(asctime)s  %(name)s.%(funcName)s  %(levelname)s: %(message)s',
                              datefmt='%Y-%m-%dT%H:%M:%S')
consoleHandler.setFormatter(formatter)

global message_received


class SwitchMQTT:
    def __init__(self, host_address: str, username: str, password: str, session_id: str,
                 client_id: str, email: str, project_id: str, installation_id: str, host_port: int = WS_DEFAULT_PORT):
        """Constructor for MQTT Message Broker client.

        Parameters
        ----------
        host_address : str
            MQTT message broker host address.
        host_port :int
            MQTT message broker port. Defaults to 443.
        username : str
            MQTT credentials - username.
        password :str
            MQTT credentials - password.
        session_id : str
            Unique Session Id for connection.
        client_id : str
            Unique Client Id for connection.
        email : str
            User email requesting Control.
        project_id : str
            Portfolio to connect for control request.
        installation_id : str
            Installation to connect for control request.
        """
        self.host_address = host_address
        self.port = host_port
        self.client_id = client_id.lower()
        self.session_id = session_id
        self.email = email
        self.project_id = project_id
        self.installation_id = installation_id
        self.is_connected = False
        self.is_gateway_connected = False
        self.request_status = 0
        self.connection_timeout = WS_MQTT_CONNECTION_TIMEOUT

        self.sensor_request_count = 0
        self.sensor_request: list[dict] = []
        self.sensor_results: list[dict] = []

        self.mqttc = mqtt.Client(client_id=client_id, transport='websockets')
        self.mqttc.tls_set()
        self.mqttc.username_pw_set(username, password)
        self.mqttc.on_connect = self._on_connect
        self.mqttc.on_message = self._on_message

    def _on_connect(self, client: mqtt.Client, userdata: any, flags: dict, rc: int):
        """Event callback when connecting to the MQTT Message Broker

        Parameters
        ----------
        client: mqtt.Client
            The client instance for this callback
        userdata: any
            The private user data as set in Client() or user_data_set(). None for this workflow. 
        flags: dict
            Response flags sent by the broker
        rc: int
            The connection result
        """
        if rc == 0:
            logger.info(
                f"Connected to MQTT broker: {self.host_address} port:{self.port}")

            topics_to_subscribe = [
                {"topic": self.client_id, "qos": 1},
                # {"topic": f"control-result/pid/{self.project_id}/site/{self.installation_id}", "qos": 1},
                {"topic": f"state/pid/{self.project_id}/site/{self.installation_id}/#", "qos": 1},
            ]

            for topic in topics_to_subscribe:
                url = topic["topic"]
                qos = topic["qos"]
                logger.info(f"Subscribing to topic: {url}     qos:{qos}")
                self.subscribe(topic=url, qos=qos)

            self.is_connected = True
        else:
            logger.error(f"Connection failed with code {rc}")

    def _on_message(self, client: mqtt.Client, userdata: any, message: MQTTMessage):
        """Event callback when a message received by the client

        Parameters
        ----------
        client: mqtt.Client
            The client instance for this callback
        userdata: any
            The private user data as set in Client() or user_data_set(). None for this workflow. 
        message: MQTTMessage
            An instance of MQTTMessage. This is a class with members topic, payload, qos, retain.
        """
        payload_str = message.payload.decode()
        payload = json.loads(payload_str)

        topic = message.topic
        action = payload.get('action')

        if topic == self.client_id and action == CONTROL_REQUEST_ACTION_ACK:
            self._process_acknowledgement(payload=payload)
            self._process_write_acknowledgement(payload=payload)
        # elif topic == f'control-result/pid/{self.project_id}/site/{self.installation_id}' and action == CONTROL_REQUEST_ACTION_RESULT:
        #     self._process_notification(payload=payload)
        elif topic.startswith('state/pid') and topic.endswith('svc/janus'):
            self._process_gateway_connected(payload=payload)

    def connect(self, timeout: int = WS_MQTT_CONNECTION_TIMEOUT) -> bool:
        """Initiate connection to MQTT Broker.

        Parameters
        ----------
        timeout : int, Optional
            Timeout in seconds for trying to connect to MQTT Message Broker.
                Defaults to WS_MQTT_CONNECTION_TIMEOUT.
        """
        self.connection_timeout = timeout
        url = urlparse(self.host_address)

        logger.info(
            f'Attempting connection to MQTT broker with client_id={self.client_id} on host={self.host_address} port={self.port}')
        logger.info(f'hostname={url.hostname}')

        self.mqttc.connect(host=url.hostname, port=self.port)
        self.mqttc.loop_start()

        start_time = time.time()
        while not self.is_connected and not self.is_gateway_connected and time.time() - start_time < timeout:
            time.sleep(WS_MQTT_WAIT_TIME_INTERVAL)

        return self.is_connected

    def send_control_request(self, sensors: list[dict]):
        """Sends control-request action to Switch MQTT Broker to request control

        Parameters
        ----------
        topic : str
            Message broker topic to pulish message to
        sensors : dict
            Sensors to request control and update value
        """
        logger.info(f'Sending Control Request for {sensors}')

        self.sensor_results = []
        self.sensor_request = sensors
        self.sensor_request_count = len(sensors)
        topic = f'control/pid/{self.project_id}/site/{self.installation_id}'

        payload = self._build_control_request_payload(sensors=sensors)
        payload_json = json.dumps(payload)

        logger.info(f'Payload = {payload_json}')
        self.mqttc.publish(topic=topic, payload=payload_json)

        start_time = time.time()
        while len(self.sensor_results) < self.sensor_request_count and time.time() - start_time < self.connection_timeout:
            time.sleep(WS_MQTT_WAIT_TIME_INTERVAL)

        if len(self.sensor_results) == self.sensor_request_count:
            logger.info("All Sensor Control Request received.")
        else:
            logger.info("Timeout reached.")

        logger.info('Checking missing items...')

        sensor_ids_received = set(item['sensorId']
                                  for item in self.sensor_results)

        missing_items = [item for item in sensors if item['sensorId']
                         not in sensor_ids_received]

        for item in missing_items:
            item['writeStatus'] = "Timeout reached"

        if len(missing_items) == 0:
            logger.info('There are no missing items.')
        else:
            logger.info(f'There are {len(missing_items)} missing items.')

        return pandas.DataFrame(self.sensor_results), pandas.DataFrame(missing_items)

    def subscribe(self, topic: str, qos: int = 0):
        """Subscribes to topic.

        Parameters
        ----------
        topic : str
            Topic for Websocket subscription.
        qos: int (optional)
            Defaults to 0
            Quality of Service (QoS) in MQTT messaging is an agreement between sender and receiver on the guarantee of delivering a message.
            There are three levels of QoS:
            0 - at most once
            1 - at least once
            2 - exactly once
        """
        self.mqttc.subscribe(topic=topic, qos=qos)

    def disconnect(self):
        """Disconnect connection to MQTT Message Broker.
        """
        self.mqttc.disconnect()
        self.mqttc.loop_stop()

    def _process_acknowledgement(self, payload: dict):
        """Process mqtt message for control result acknowledgement

        Parameters
        ----------
        payload : dict

            Message payload
        """
        status_messages = {
            0: "Appliance doesn't have any of the sensors requested.",
            1: "Appliance will control some of the sensors in the requested list.",
            2: "Appliance will control all the sensors in the list."
        }

        status = payload.get("status", -1)
        logger.info(
            f'Control Request Acknowledgment. Mac={payload["mac"]} Status={status_messages.get(status, "Unknown status")}')

        self.request_status = status

    def _process_write_acknowledgement(self, payload: dict):
        """Process mqtt message for control result acknowledgement as write command successful
        and return sensor list request sent as a response.

        Parameters
        ----------
        payload : dict

            Message payload
        """

        for item in self.sensor_request:
            sensor_control_result = {
                'sensorId': item["sensorId"],
                'controlValue': item["controlValue"],
                'presentValue': item["controlValue"],
                'defaultControlValue': item.get("defaultControlValue", None),
                'priority': item["priority"],
                'status': 1,
            }

            self.sensor_results.append(sensor_control_result)

    def _process_notification(self, payload: dict):
        """Process mqtt message for control result notification

        Parameters
        ----------
        payload : dict
            Message payload
        """
        write_status = payload.get('status', -1)
        write_status_description = {
            0: 'Write success - session in progress',
            1: 'Write success - session completed',
            2: 'Write failed - session failed',
            3: 'Read verification failed - session failed'
        }.get(write_status, 'Unknown Write Status')

        logger.info(
            f'Sensor {payload["sensorId"]} Value={payload["presentValue"]}, Status={write_status_description}')

        sensor_control_result = {
            'sensorId': payload["sensorId"],
            'controlValue': payload["controlValue"],
            'presentValue': payload["presentValue"],
            'defaultControlValue': payload.get("defaultControlValue", None),
            'status': write_status,
        }

        if not write_status == 0:
            self.sensor_results.append(sensor_control_result)

    def _build_control_request_payload(self, sensors: dict):
        """Util function to build control request payload to Switch MQTT Broker

        Parameters:
        sensors (dict): 
            List of sensors to request control

        Returns:
            _type_: _description_
        """
        return {
            'action': 'control-request',
            'clientId': self.client_id,
            'originator': self.email,
            'sensors': sensors,
            'sessionId': str(self.session_id)
        }

    def _process_gateway_connected(self, payload: dict):
        """Process mqtt message for control result acknowledgement

        Parameters
        ----------
        payload : dict
            Message payload
        """

        self.is_gateway_connected = payload.get('status', False)
        logger.info(f'Gateway Connected Status={self.is_gateway_connected}')
