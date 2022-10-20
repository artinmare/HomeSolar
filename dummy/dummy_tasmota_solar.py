#This dummy used for emulate solar production reading from DC Power Meter by Tasmota

import threading
from paho.mqtt import client as mqttClient
from time import sleep, gmtime
import json
import random
import calendar
from datetime import datetime

#Setup MQTT Client
client = mqttClient.Client()

#Initialize Constants and data
device_name = "dummy_tasmota_solar"
isDebug = True

#Custom Helper Class to contains all Mqtt related values
class MqttHelper:
    TOPIC_SENSORS = f"homesolar/sensors/{device_name}"
    HOST = "localhost"
    PORT = 1883
    TIMEOUT = 60
    USERNAME = device_name
    PASSWORD = f"{device_name}_123"


#Custom print function
def debug(message):
    if(isDebug):
        print(f"{device_name} \033[1;32mDEBUG\033[0m {message}")

#Setup Callbacks
def onConnect(client, userdata, flags, rc):
    debug("Connected to MQTT Broker")
    # Subscribe to Actuator Topic to recive commands
    try:
        debug("No topics to subscribed to")
    except:
        debug("Subcribe failed")

def onMessage(client, userdata, msg):
    #Get the payload if there is anything send to the Actuator Topic 
    payload = msg.payload
    debug(f"Receiving command!\n\t{payload}")

    #Here I assume that the input is a json, so if it's not it's ignored
    try:
        #get the commands in a dict format from a json
        commands = json.loads(payload)

        try:
            debug("No command expected, ignored!")
        except Exception as e:
            debug(f"Executing commands failed! Reason: {e}")
        
    except:
        debug("Not a valid command, ignored!")

#Setup data collections sequence
def runDataCollection():
    while True:
        try:
            #Make random data
            current = random.randint(1,1000)/100
            voltage = random.randint(490,510)/10
            today = random.randint(4000,6000)/1000
            yesterday = random.randint(4000,6000)/1000

            # Current GMT time in a tuple format
            current_GMT = gmtime()

            # ts stores timestamp
            ts = calendar.timegm(current_GMT)

            time = datetime.fromtimestamp(ts, tz=None)

            payloadState = {
                        "Time":str(time),
                        "Uptime":"329T05:38:27",
                        "UptimeSec":28445907,
                        "Heap":27,
                        "SleepMode":"Dynamic",
                        "Sleep":50,
                        "LoadAvg":19,
                        "MqttCount":747,
                        "POWER":"ON",
                        "Wifi":
                        {
                            "AP":1,
                            "SSId":"ZTE",
                            "BSSId":"34:78:39:7B:0D:12",
                            "Channel":1,
                            "RSSI":100,
                            "Signal":-32,
                            "LinkCount":13,
                            "Downtime":"0T03:10:27"
                        }
                    }
            
            payloadSensor = {
                        "Time":str(time),
                        "ENERGY":
                        {
                            "TotalStartTime":"2021-06-06T02:47:42",
                            "Total":today*yesterday,
                            "Yesterday":yesterday,
                            "Today":today,
                            "Period":0,
                            "Power":voltage*current,
                            "Voltage":voltage,
                            "Current":current
                        }
                    }

            #Send the data
            client.publish(topic=MqttHelper.TOPIC_SENSORS + "/STATE", payload=json.dumps(payloadState))
            client.publish(topic=MqttHelper.TOPIC_SENSORS + "/SENSOR", payload=json.dumps(payloadSensor))
            sleep(5)
        except Exception as e:
            debug(f"Something went wrong with the data collection! Reason: {e}")

#Setup run sequence
def run():
    try:
        debug(f"Connecting to MQTT Broker on {MqttHelper.HOST}:{MqttHelper.PORT}")    
        #Run the MQTT Client
        client.on_connect = onConnect
        client.on_message = onMessage
        client.reconnect_delay_set(min_delay=1, max_delay=120)
        client.username_pw_set(username=MqttHelper.USERNAME, password=MqttHelper.PASSWORD)
        client.connect(host=MqttHelper.HOST, port=MqttHelper.PORT)

        #Run data collection loop as a different thread
        data_collection_thread = threading.Thread(target=runDataCollection, args=(), daemon=True)
        data_collection_thread.start()

        #run the MQTT loop so the client stay connected
        client.loop_forever()
    except Exception as e:
        debug(f"Failed to connect! Reason: {e}")
        debug("Retrying in 5 seconds, press ctrl+c to stop the program!\n")

        #Handle ctrl+c
        try:
            sleep(5)
        except:
            exit()

        #Try closing the threads before re-run
        try:
            data_collection_thread.join()
        except:
            pass
        
        #Re-run the program
        run()    

#Run the dummy device
if __name__ == "__main__":
    debug(f"{device_name} started!")
    run()
