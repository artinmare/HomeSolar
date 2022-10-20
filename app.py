#Others Library imports
from loguru import logger
from time import sleep
import threading

#App Packages Imports
from services.mqtt import AppClient
from modules.database import *

#global values
mqttService = AppClient()

#Get the logger from utils
def main_start():
    try:
        logger.info("Initiating main start sequence")

        #Run each sevices as a different thread
        #Run MQTT Service
        logger.info("Starting MQTT Service...")
        mqtt_service_thread = threading.Thread(target=mqttService.start(), args=(), daemon=True)
        mqtt_service_thread.start()
        logger.info("MQTT Service started successfully")

        logger.info("Start sequence is executing successfully, app is now running!")
        #Do nothing and lock the main thread so the app would no close until something went wrong or closed by the user
        while True:
            pass

    except Exception:
        logger.exception("Something when wrong when initiating main start sequence")
        logger.warning("Restarting the app, please CTRL+C to stopped the process!")

        try:
            sleep(5)
        except:
            logger.info("App is closing...")
            exit()

        #Re run the program
        main_start()

#Check if app.py is running as an app, if so start the program
if __name__ == "__main__":
    logger.info("App is starting up...")
    main_start()