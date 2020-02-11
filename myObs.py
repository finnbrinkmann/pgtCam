#!/usr/bin/python3


import datetime 
import time 
import threading
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from log import logWatchdog as logW
from readConfig import readConfig as readConfig


#this file provides a backup system for the camera recording. It checks if there are files recorded

class MyHandler(FileSystemEventHandler):

    shutdownTime = datetime.datetime.now()
    interval = 15

    def __init__(self):
    

        self.shutdownTime = datetime.datetime.now()  + datetime.timedelta(minutes = 35) #wait 35 min at the beginning
        #self.doomsdayClock()
        t = threading.Thread(target=self.doomsdayClock) # starting as a thread
        t.start()
        
        #readCondig
        configFile = "/home/pi/defaultConfig.txt"
        an, aus, fps, rot, resX, resY, self.interval, powersave, ipAddress, stromPi, kName, bw, receiver, encrypt, zero = readConfig(configFile, None, None, None, None, None, None, self.interval, None, None, None, None, None, None, None, None)
        
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
                        an, aus, fps, rot, resX, resY, interval, powersave, ipAddress, stromPi, kName, bw, receiver, encrypt, zero = readConfig(configFile, None, None, None, None, None, None, self.interval, None, None,None, None, None, None, None, None)
                        
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
            
        os.system('sudo reboot')

    def on_created(self, event):
        print(f'event type: {event.event_type}  path : {event.src_path}')
        self.shutdownTime = datetime.datetime.now()  + datetime.timedelta(minutes = self.interval + 5) # 20 min more time to create a new file
        print(self.shutdownTime)


if __name__ == "__main__":
    
    #time.sleep(5*60) # wait 5min to boot up the rest
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