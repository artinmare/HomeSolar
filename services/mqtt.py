#Others packages imports
from loguru import logger
import paho.mqtt.client as mqtt
import json
import asyncio

#Project packages imports
from common import utils
from common import constants as cons
from modules import database
from modules import controls
# from modules import controls

#Simple enum-like class for saving MQTT Topics
class MqttTopic:
    SENSORS = "homesolar/sensors/#"
    ACTUATORS = "homesolar/actuators/#"
    CLIENT = "homesolar/app/clients/#"
    REQUEST = "homesolar/app/request/#"
    RESPONSE = "homesolar/app/response"
    SUMMARY = "homesolar/summary"

#Make a class to handle MQTT Sevice
class AppClient:
    __metaclass__ = utils.Singleton
    client = mqtt.Client()
    
    @staticmethod
    def onMessage(client, userdata, msg):
        #Check what topic the message is recieved at
        #Using if elif since python do not have switch until python 3.10
        logger.debug(f"Topic: {msg.topic}, Payload: {msg.payload}")

        #Handles messages on Sensors Topic
        if(MqttTopic.SENSORS[:-2] in str(msg.topic)):
            sensor_name = str(msg.topic).replace(MqttTopic.SENSORS[:-2] + "/", "")
            
            try:
                payload = json.loads(msg.payload)
                fields = utils.flattenListOrDict(payload)
            except:
                fields = {"value": str(msg.payload.decode("utf-8"))}
                
            logger.debug(f"Measurement: {sensor_name}\nFields: {fields}")
            data = {
                "measurement": sensor_name,
                "fields": fields
            }
            asyncio.run(database.influxDBWriteData(data))
            # asyncio.run(sqliteWriteOrUpdate(data, type = "Parameter"))
            asyncio.run(controls.checkControls(client, data))

        #Handles messages on Actuators Topic
        #Currently does nothing with the status send back by actuators
        elif(MqttTopic.ACTUATORS[:-2] in str(msg.topic)):
            pass

        #Handles messages on Request Topic
        #Currently only handlas Settings Update and Statistics Request
        elif(MqttTopic.REQUEST[:-2] in str(msg.topic)):
            pass

    @staticmethod
    def onConnect(client, userdata, flags, rc):
        logger.info("Connected to MQTT Broker")

        #Subscribes to All Topics
        try:
            client.subscribe(MqttTopic.SENSORS)
            client.subscribe(MqttTopic.ACTUATORS)
            client.subscribe(MqttTopic.REQUEST)
            client.subscribe(MqttTopic.CLIENT)
            logger.info("All topics is subscribed")
        except:
            logger.exception("Something went wrong, some subcribe may failed")
        
    def start(self):
        self.client.reconnect_delay_set(min_delay=1, max_delay=120)
        self.client.on_connect = self.onConnect
        self.client.on_message = self.onMessage

        self.client.connect(cons.MQTT_SERVER_IP, cons.MQTT_SERVER_PORT, 60)
        self.client.loop_forever()