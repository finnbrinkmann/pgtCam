#!/usr/bin/python3


import datetime 
import time 
import threading
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from log import logWatchdog as logW
import yaml


#this file provides a backup system for the camera recording. It checks if there are files recorded

class MyHandler(FileSystemEventHandler):

    shutdownTime = datetime.datetime.now()
    interval = 15

    def __init__(self):
        
        #cut down version of readConfig.py. Just read the interval length
        def readConfigObs(self, filename):
            
            configFile = None
            content = {}

            try:
                if(os.path.isfile(filename)):
                    configFile = open(filename, "r")
                    print("INFO: " + str (filename) + " geöffnet")
                else:
                    print ("WARNING: Kann Datei nicht lesen " + filename + ". Datei nicht vorhanden.")
            except Exception as e:
                print ("ERROR: Kann Datei nicht lesen " + filename + ". Datei vorhanden? " + str(e))
            try:
                if (configFile != None):
                    content = yaml.load(configFile, Loader=yaml.FullLoader) # read config file in yaml format
            except Exception as e:
                print("ERROR: Fehler in lesen der Config Datei! " + str(e))

            #log config file
            if content:
                if "interval" in content:
                    try:
                        self.interval = int(content["interval"])
                    except ValueERROR as e:
                        logW("ERROR: Interval config.txt Wert ist keine Zahl. Benutze Default Wert" + str(e))  
                        
                

        self.shutdownTime = datetime.datetime.now()  + datetime.timedelta(minutes = 35) #wait 35 min at the beginning
        #self.doomsdayClock()
        t = threading.Thread(target=self.doomsdayClock) # starting as a thread
        t.start()
        
        #readCondig
        configFile = "/home/pi/defaultConfig.txt"
        readConfigObs(self,configFile)
        
        paths = ["/media/ntfs/","/media/vFat/","/media/exFat/"] # all possible mount points; check /etc/fstab
        stickFound = False
        while not stickFound: #loopbreak until a stick is found
            
            for x in paths:
                
                if os.path.ismount(x):
                    print("INFO: Mountpunkt ist: " + str(x))
                    path = x
                    try:
                        configFile = str(x) + "config.txt"
                        print(configFile)
                        readConfigObs(self,configFile)
                        
                    except Exception as e:
                        print ("WARNING: Kann Datei nicht lesen " + x + "config.txt. Datei vorhanden? " + str(e))
                        
                    stickFound = True
            if not stickFound:
                
                sleep(5)
                print ("INFO: Kein USB-Stick gefunden")
                #exit()
        
        print("Handler init complete")

        
    def doomsdayClock(self):
        while datetime.datetime.now() < self.shutdownTime:
            time.sleep(30)
            
        try:
            logW ("ERROR: Ein Fehler ist aufgetreten. Es wurde keine Dateien mehr angelegt! Starte Neu!")
            logW (datetime.datetime.now())
            time.sleep(10)
            
        except Exception as e:
            print("ERROR: watchdog " + str(e))
            
        os.system('sudo reboot') # reboot and hope this will fix the error.

    def on_created(self, event):
        print(f'event type: {event.event_type}  path : {event.src_path}')
        self.shutdownTime = datetime.datetime.now()  + datetime.timedelta(minutes = self.interval + 5) # 20 min more time to create a new file
        print(self.shutdownTime)


if __name__ == "__main__":
    
    time.sleep(30*60) # wait 30min skip start period
    event_handler = MyHandler()
    
    observer = Observer()
    
    #observer.schedule(event_handler, path='/mount/media/', recursive=True)
    observer.schedule(event_handler, path='/media/', recursive=True)
    
    observer.start()

    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()