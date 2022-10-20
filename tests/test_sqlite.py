#Load all params save in sqlite

#3rd party imports
import asyncio
from loguru import logger
from interfaces.sqlite import getConditions, getParameters, resetTable, updateConditions, updateParameters

#Local imports
from modules import database
from common import utils
from modules.models import Condition

async def read_params():
    result = await getParameters()
    for param in result:
        attrs = vars(param)
        logger.debug(', '.join("%s: %s" % item for item in attrs.items()))

async def insert_params():
    values = {
            "A":1,
            "B":"Wasdasdawawa",
            "C":141.234,
            "D":5343,
            "E":"E",
            "F":"F",
            "G":"G"
    }
    await updateParameters(values)

async def read_conditions():
    result = await getConditions()
    for param in result:
        attrs = vars(param)
        logger.debug(', '.join("%s: %s" % item for item in attrs.items()))
    # table = "condition"
    # field = "*"
    # result = await (database.sqliteRead(table=table, fields=field))
    # for row in result:
    #     logger.debug(row)
    
async def insert_condition():
    table = "condition"
    values = [
        {
            "name" : "Test Condition A",
            "description" : "This is a test condition only for testing / debugging purpose (A)",
            "values" : [
                {"parameter" : "sensor_name#sensor_field", "operator": ">=", "value": "10", "extra": "AND"},
                {"parameter" : "sensor_name#sensor_field", "operator": ">=", "value": "10", "extra": "OR"},
                {"parameter" : "sensor_name#sensor_field", "operator": ">=", "value": "10", "extra": "NONE"}
            ],
            "actions":[
                {
                    "type":"MQTT", 
                    "value":{
                        "topic": "homesolar/actuators/sensor_name",
                        "payload": {
                            "GPIO_1" : "Turn On"
                        }
                    },
                    "type":"GPIO", 
                    "value":{
                        "port": 1,
                        "active": "HIGH",
                        "action": "Turn On"
                    }
                }
            ]
        },
        {
            "id": 12,
            "name" : "Test Condition B",
            "description" : "This is a test condition only for testing / debugging purpose (B)",
            "value" : [
                {"parameter" : "sensor_name#sensor_field", "operator": ">=", "value": "10", "extra": "AND"},
                {"parameter" : "sensor_name#sensor_field", "operator": ">=", "value": "10", "extra": "OR"},
                {"parameter" : "sensor_name#sensor_field", "operator": ">=", "value": "10", "extra": "NONE"}
            ],
            "actions":[
                {
                    "type":"MQTT", 
                    "value":{
                        "topic": "homesolar/actuators/sensor_name",
                        "payload": {
                            "GPIO_1" : "Toggle"
                        }
                    },
                    "type":"GPIO", 
                    "value":{
                        "port": 2,
                        "active": "LOW",
                        "action": "Toggle"
                    }
                }
            ]
        }
    ]
    await updateConditions(values)
    #result = await (database.sqliteWrite(table=table, values=values))

if __name__ == "__main__":
    #asyncio.run(database.sqliteResetDB())
    asyncio.run(insert_params())
    asyncio.run(read_params())
    asyncio.run(insert_condition())
    asyncio.run(read_conditions())
    asyncio.run(resetTable(Condition))