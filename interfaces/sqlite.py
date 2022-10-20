#3rd party imports
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

#local imports
from modules import database
from modules.models import Action, Condition, ConditionValue, Parameter

#Describe the all the possible interface for communicating with Sqlite for controls purpose
async def getConditions():
    #Get all the conditions available
    async with database.sqliteSession() as session:
        
        stmt = select(Condition).options(selectinload(Condition.actions))
        result = await session.execute(stmt)

        return result.scalars()

async def updateConditions(details: list):
    #Delete existing conditions first
    async with database.sqliteSession() as session:
        ids = []
        for condition in details:
            if("id" in condition.keys()):
                ids.append(condition['id'])

        stmt = select(Condition).filter(Condition.id.in_(ids)).options(selectinload(Condition.actions),selectinload(Condition.values))
        result = await session.execute(stmt)

        remainingConditions = details.copy()
        for id, condition in enumerate(result.scalars()):
            if condition.id != details[id]['id']:
                continue
            
            newActions = details[id]["actions"]
            remainingActions = newActions.copy()
            newConditionActionsLength = len(newActions)
            for idx, action in enumerate(condition.actions):
                if idx < newConditionActionsLength:
                    action.type = newActions[idx]['type']
                    action.value = newActions[idx]['value']
                    remainingActions.pop(0)
                else:
                    del condition.actions[idx]                   
                
            newValues = details[id]["values"]
            remainingValues = newValues.copy()
            newConditionValuesLength = len(newValues)
            for idx, value in enumerate(condition.values):
                if idx < newConditionValuesLength:
                    value.parameter = newValues[idx]['parameter']
                    value.operator = newValues[idx]['operator']
                    value.value = newValues[idx]['value']
                    value.extra = newValues[idx]['extra']
                    remainingValues.pop(0)
                else:
                    del condition.values[idx]

            for action in remainingActions:
                session.add(Action(type=action['type'], value=action['value']))

            for value in remainingValues:
                session.add(ConditionValue(parameter=value['parameter'], operator=value['operator'], value=value['value'], extra=value['extra']))
    
            remainingConditions.pop(0)
        await session.commit()


async def getParameters(details = None):
    async with database.sqliteSession() as session:
        
        stmt = select(Parameter)
        result = await session.execute(stmt)
        
        return result.scalars()

async def updateParameters(details: dict):
    #Update or Add new parameters to database
    async with database.sqliteSession() as session:
        keys = details.keys()

        stmt = select(Parameter).filter(Parameter.field.in_(list(keys)))
        result = await session.execute(stmt)

        for parameter in result.scalars():
            newValue = details[parameter.field]
            if(parameter.value != newValue):
                parameter.value = newValue
            details.pop(parameter.field)
                

        for key, value in details.items():
            session.add(Parameter(field=key,value=value))

        await session.commit()

async def resetDB():
    pass

async def resetTable(table):
    async with database.sqliteSession() as session:
        stmt = select(table)
        result = await session.execute(stmt)

        for row in result.scalars():
            await session.delete(row)

        await session.commit()