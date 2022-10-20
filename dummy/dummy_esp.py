#This dummy is used for simple sensor reading and relay control
#It's emulate a function of an esp but without the WiFi setup

import threading
from paho.mqtt import client as mqttClient
from time import sleep
import json
import random

#Setup MQTT Client
client = mqttClient.Client()

#Initialize Constants and data
device_name = "dummy_esp"
isDebug = True

#Custom Helper Class to contains all Mqtt related values
class MqttHelper:
    TOPIC_SENSORS = f"homesolar/sensors/{device_name}"
    TOPIC_ACTUATORS = f"homesolar/actuators/{device_name}"
    HOST = "localhost"
    PORT = 1883
    TIMEOUT = 60
    USERNAME = device_name
    PASSWORD = f"{device_name}_123"

#Make custom class for relays
class Relay():
    name = "Relay"
    status = "OFF"
    onStatusChange = None

    #Set values during initialization to properties
    def __init__(self, name):
        self.name = name

    #Dummy signal, just print the output. On the real ESP it would just send a signal to it's GPIO
    def sendSignal(self, signal):
        debug(f"{self.name} is now {signal}")

        #Do something if there is a callback setup
        if(self.onStatusChange):
            self.onStatusChange

    #Check if current status is the same with the input, if not change the status and send the signal
    def check(self, status):
        if(self.status != status):
            self.status = status
            return self.sendSignal(status)
        debug(f"Command ignored, {self.name} is already {self.status}")

    #Turn on the relay    
    def turnOn(self):
        debug(f"{self.name} is being Turned ON")
        self.check("ON")

    #Turn off the relay
    def turnOff(self):
        debug(f"{self.name} is being Turned OFF")
        self.check("OFF")

    #Toggle the relay
    def toggle(self):
        debug(f"{self.name} is being Toggled")
        if(self.status == "ON"):
            return self.check("OFF")
        self.check("ON")

    #Recieve Command
    def do(self, command):
        if(command == "ON"):
           return self.turnOn()
        if(command == "OFF"):
           return self.turnOff()
        if(command == "Toggle"):
           return self.toggle()
        debug(f"{self.name}: Unknown command, ignored!")


#Custom print function
def debug(message):
    if(isDebug):
        print(f"{device_name} \033[1;32mDEBUG\033[0m {message}")

#Setup Callbacks
def onConnect(client, userdata, flags, rc):
    debug("Connected to MQTT Broker")
    # Subscribe to Actuator Topic to recive commands
    try:
        client.subscribe(MqttHelper.TOPIC_ACTUATORS)
        debug("All topics is subscribed")
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
            debug("Trying to execute the commands")
            #Now that we got the commands, we can use that to do certain actions
            #This time I assume that the dummy device only have specific amount of actions
            #These are controlling two relays

            if("relay_1" in str(commands)):
                relay1_command = str(commands["relay_1"])
                #Manually select the action
                if(relay1_command == "ON"):
                    relay1.turnOn()
                elif(relay1_command == "OFF"):
                    relay1.turnOff()
                elif(relay1_command == "Toggle"):
                    relay1.toggle()
                else:
                    debug(f"{relay1.name}: Unknown command, ignored!")
            
            if("relay_2" in str(commands)):
                relay2_command = str(commands["relay_2"])
                #Automaticly select the action
                relay2.do(relay2_command)

            debug("All commands executed successfully!")
        except Exception as e:
            debug(f"Executing commands failed! Reason: {e}")
        
    except:
        debug("Not a valid command, ignored!")

#Initialize Relays
relay1 = Relay("Relay 1")
relay2 = Relay("Relay 2")

#Setup data collections sequence
def runDataCollection():
    while True:
        try:
            #Make random data
            data = random.randint(1,1000)
            payload = {}
            payload["data"] = data

            #Send the data
            client.publish(topic=MqttHelper.TOPIC_SENSORS, payload=json.dumps(payload))
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
    debug("Dummy started!")
    run()
