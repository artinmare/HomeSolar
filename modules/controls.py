#This module keep track of actions to do when certain conditionas are triggred.
from paho.mqtt.client import Client

#Local imports
from modules import database

gpios = []
#Try importing GPIO if on raspberry pi
try:
    import RPi.GPIO as GPIO
    rpi_platform = True
except:
    rpi_platform = False

async def checkControls(client: Client, data):
    pass
    # client.publish("homesolar/testing", "Send from controls succesfully")

# async def checkConditions(data):
#     #Query all the conditions available
#     for condition in s.query(Condition):
#         print(type(condition), condition.id, condition.name, condition.description, condition.value, condition.actions)
#         for action in condition.actions:
#             print(type(action), action.id, action.type, action.value)

# #Add new condition to the database
# def addCondition(details):
#     condition_desc = details["description"] if("description" in details) else None
#     condition = Condition(name=details["name"], description=condition_desc, value=details["value"])

#     for action in details["actions"]:
#         temp_action = Action(type=action["type"], value=json.dumps(action["value"]))
#         condition.actions.append(temp_action)
#     s.add(condition)
#     s.commit()

#Setup server controls (Have to manually describe in code, would be updated to automatic in later version)
def setupGpio():
    if(rpi_platform):
        GPIO.setmode(GPIO.BCM)
        
        newGpios = getGpios()
        for gpio in gpios:
            if(gpio in newGpios):
                continue
            else:
                GPIO.cleanup(gpio)
                gpios.remove(gpio)

        for newGpio in newGpios:
            if(newGpio in gpios):
                continue
            else:
                GPIO.output(newGpio, GPIO.LOW)

async def getGpios():
    pass
# #Start the service when called
# def run():
#     dummy_conditions = '''
#         {
#             "conditions": [
#                 {
#                     "name": "Condition A",
#                     "description": "Turn on Lamp when Battery is more than 50%",
#                     "value": "bms/value&>=&50.0&or&bms/value&<=&80.0",
#                     "actions": [
#                         {
#                             "type": "MQTT",
#                             "value": {
#                                 "topic": "homesolar/actuators/dummy_esp",
#                                 "payload": {
#                                     "relay_1": "ON",
#                                     "relay_2": "Toggle"
#                                 }
#                             }
#                         }
#                     ]
#                 },
#                 {
#                     "name": "Condition B",
#                     "value": "bms/value&>&80.0",
#                     "actions": [ 
#                         {
#                             "type": "ServerCommand",
#                             "value": {
#                                 "GPIO1": "ON"
#                             }
#                         }
#                     ]
#                 }
#             ]
#         }
#     '''  
#     details = json.loads(dummy_conditions)
#     for condition in details["conditions"]:
#         addCondition(condition)

#If run directly (Debugging purposes)
# if __name__ == "__main__":

#     #Query test and print the dummy_esp
#     for condition in s.query(Condition):
#         print(type(condition), condition.id, condition.name, condition.description, condition.value, condition.actions)
#         for action in condition.actions:
#             print(type(action), action.id, action.type, action.value)