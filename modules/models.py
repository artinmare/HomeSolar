#This module is used for defining the Database Scheme for SQLite
#Others library imports
from sqlalchemy import Column, Integer, Unicode, UnicodeText, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

#Create a sqlite database if not exist and connect with it
sqliteBase = declarative_base()

class Condition(sqliteBase):
    __tablename__ = "condition"
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(40))
    description = Column(UnicodeText, nullable=True)
    values = relationship(
        "ConditionValue",
        cascade="all, delete, delete-orphan",
        passive_deletes=True,
    )
    actions = relationship(
        "Action",
        cascade="all, delete, delete-orphan",
        passive_deletes=True,
    )
    
    #Name: Whatever name you want to use to identify the condition
    #Description: Whatever description you want to use to discribes the condition
    #Valuse: The list of parameter value that would be check againts the sensor data
    #Actions: The list of actions taken when said condition is fullfiled

class ConditionValue(sqliteBase):
    __tablename__ = "condition_value"
    id = Column(Integer, primary_key=True)
    parameter = Column(Unicode(200))
    operator = Column(Unicode(3))
    value = Column(UnicodeText)
    extra = Column(Unicode(5))
    condition_id = Column(Integer, ForeignKey("condition.id", ondelete="CASCADE"))

    #Value format
    # [
    #     {"parameter" : "sensor_name[sensor_field]", "operator": ">=", "value": "10", "extra": "AND"},
    #     {"parameter" : "sensor_name[sensor_field]", "operator": ">=", "value": "10", "extra": "OR"},
    #     {"parameter" : "sensor_name[sensor_field]", "operator": ">=", "value": "10", "extra": "NONE"}
    # ]

#Make custom class for the actions
class Action(sqliteBase):
    __tablename__ = "action"
    id = Column(Integer, primary_key=True)
    type = Column(Unicode(40))
    value = Column(UnicodeText)
    condition_id = Column(Integer, ForeignKey("condition.id", ondelete="CASCADE"))

    #Type Available:
    # GPIO
    # MQTT

    #Value Format for GPIO
    # {
    #     "GPIO": 1,                #BCM Numbering, would only execute if the server is a Raspberry Pi
    #     "action": "Turn On",      #What to do for the GPIO, Turn On, Turn Off or Toggle
    #     "active": "HIGH"          #When the GPIO is said as ACTIVE is it on HIGH or LOW signal
    # }

    #Value format for MQTT
    # {
    #     "topic": "whatever/topic/wanted/ex/homesolar/actuators/test",
    #     "payload": "whatever action you want, preferabbly a json"
    # }

#Make custom class for saving most recent data used for controls
class Parameter(sqliteBase):
    __tablename__ = "parameter"
    id = Column(Integer, primary_key=True)
    field = Column(Unicode(200), unique=True)
    value = Column(UnicodeText)

    #Below is 141 chars example, so the field restriction (200 chars) should suffice for extra long device and field name
    #whatever_you_can_think_of_as_a_name_for_a_device/and_whatever_name_you_can_think_of_for_the_field_but_is_only_half_the_length_it_able_to_fit

def getExtras(table):
    if(table == "parameter"):
        return  {
            "columns" : "(field, value)",
            "on_conflict": "ON CONFLICT (field) DO UPDATE SET value=excluded.value"
        }
    if(table == "condition"):
        return {
            "columns": "(name, description, value)",
            "on_conflict": ""
        }
    return {
        "columns": "",
        "on_conflict": ""
    }
