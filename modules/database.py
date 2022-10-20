#Others Library Imports
import asyncio
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync
from loguru import logger
from sqlalchemy import text

#Project packages imports
from common import constants as cons
from common import utils
from modules.models import *

sqliteEngine = create_async_engine("sqlite+aiosqlite:///homesolar.db", echo=True)
sqliteSession = sessionmaker(bind=sqliteEngine, expire_on_commit=False, class_=AsyncSession)

#Reset the db if needed
async def sqliteResetDB():
    async with sqliteEngine.begin() as conn:
        await conn.run_sync(sqliteBase.metadata.drop_all)
        await conn.run_sync(sqliteBase.metadata.create_all)
        await conn.commit()

#Read the DB for speciific record(s)
async def sqliteRead(table, fields, conditions = None):
    try:
        nl = '\n'
        sql = f"""
            SELECT {utils.stringifyFields(fields)}
            FROM {table}{nl + "WHERE" + {utils.stringifyConditions(conditions)} if conditions != None else ""};
        """

        async with sqliteSession.begin() as s:
            result = await s.execute(text(sql))
            await s.commit()
            await s.close()

        logger.info("Record(s) successfully fecthed!")
        return result
    except Exception:
        logger.exception("Something went wrong when trying to Fetch record(s)!")
        return []

#Write a specific records into DB
async def sqliteWrite(table, values):
    try:
        extras = getExtras(table)
        sql = f"""
            INSERT INTO {table} {extras["columns"]}
            VALUES {utils.stringifyValues(values, table, "write")}
                {extras["on_conflict"]};
        """

        async with sqliteSession.begin() as s:
            result = await s.execute(text(sql))
            await s.commit()
            await s.close()

        logger.info("A record has been created successfully!")
        return result
    except Exception:
        logger.exception("Something went wrong when trying to Write a record!")
        return []

async def sqliteUpdate(table, values, conditions):
    try:
        sql = f"""
            UPDATE {table}
            SET {utils.stringifyValues(values, table, "update")}
            WHERE {utils.stringifyConditions(conditions)};
        """

        async with sqliteSession.begin() as s:
            await s.execute(text(sql))
            await s.commit()
            await s.close()

        logger.info("A record has been updated successfully!")
    except Exception:
        logger.exception("Something went wrong when trying to Update a record!")

async def sqliteDelete(table, conditions):
    try:
        sql = f"""
            DELETE FROM {table} WHERE {utils.stringifyConditions(conditions)};
        """
        async with sqliteSession.begin() as s:
            await s.execute(text(sql))
            await s.commit()
            await s.close()

        logger.info("A record has been deleted successfully!")
    except Exception:
        logger.exception("Something went wrong when trying to Delete a record!")


async def influxDBWriteData(data = None, bucket = cons.INFLUXDB_DEFAULT_BUCKET):
    async with InfluxDBClientAsync(url=f"{cons.INFLUXDB_IP}:{cons.INFLUXDB_PORT}", token=cons.INFLUXDB_TOKEN, org=cons.INFLUXDB_ORG) as client:
        ready = await client.ping()
        logger.info(f"InfluxDB: {ready}")

        write_api = client.write_api()
        success = await write_api.write(bucket=bucket,record=data)
        if(success):
            logger.info(f"Data saved successfully!")
        else:
            logger.error(f"Something wen't wrong, fail to saved the data!")
        
