from collections.abc import MutableMapping
from loguru import logger
import json

class Colorcodes:
    pass

#Create a custom flatten function for list or dict
def flattenListOrDict(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(flattenListOrDict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def stringifyValues(values, table, type = "write"):
    try:
        if isinstance(values, str):
            return values
        if isinstance(values,list):
            string = ""
            if(table == "condition"):
                if(type == "write"):
                    for condition in values:
                        string += f"('{condition['name']}','{condition['description']}','{json.dumps(condition['value'])}'),"
                    return string[:-1]
        if isinstance(values, dict):
            string = ""
            if(table == "parameter"):
                list_values = values["fields"]
                if(type == "write"):
                    for key, value in list_values.items():
                        string += f"('{key}','{value}'),"
                else:
                    for key, value in list_values.items():
                        string += value + ","
                return string[:-1]
        raise TypeError("Invalid types inputted!")
    except:
        logger.warning("Invalid types inputted!")
        return "*"

def stringifyConditions(conditions):
    pass

def stringifyFields(fields):
    try:
        if isinstance(fields, str):
            return fields
        if isinstance(fields,list):
            string = ""
            fields_length = len(fields)
            for i, field in fields:
                string += field
                if(i != fields_length):
                    string+=","
            return string
        if isinstance(fields, dict):
            string = ""
            list_fields = fields["fields"]
            for key in list_fields.keys():
                string += key + ","
            return string[:-1]
        raise TypeError("Invalid types inputted!")
    except:
        logger.warning("Invalid types inputted!")
        return "*"

#Singleton class so only one instance can be shared throughout the application lifecycle
class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]