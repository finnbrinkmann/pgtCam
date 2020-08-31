import datetime
import yaml
#import types
import os
from log import log as log
import socket
from time import sleep
import log2

def readConfig(filename, an, aus, fps, rot, resX, resY, interval, powersave, ipAddress, stromPi, kName, bw, receiver, encrypt, zero, bitrate, sdcard):


    configFile = None
    content = {}


    try:
        if(os.path.isfile(filename)):
            configFile = open(filename, "r")
            log2.logger.info( str (filename) + " geöffnet")
        else:
            log2.logger.warning("Kann Datei nicht lesen " + filename + ". Datei nicht vorhanden.")
    except Exception as e:
        log2.logger.error("Kann Datei nicht lesen " + filename + ". Datei vorhanden? " + str(e))
    try:
        if (configFile != None):
            #content = yaml.load(configFile, Loader=yaml.FullLoader) # read config file in yaml format #old version
            content = yaml.load(configFile, Loader=yaml.FullLoader) # read config file in yaml format
    except Exception as e:
        log2.logger.error("Fehler in lesen der Config Datei! " + str(e))
        raise


    #log config file
    if content:
        try:
            for key, value in content.items():
                log2.logger.debug('\t' + str(key) + " : " + str(value))
        except Exception as e:
            log2.logger.error("Lesen von config.txt fehlerhaft " + str(e))


    # check if parameters are set in config file. Problem is, that we have to reboot the RPi in order wifi changes to become active. 
    

    if "powersave" in content:
        try:
            if int(content["powersave"]) == 1:
                powersave = True
            else:
                powersave = False
        except Exception as e:
            log2.logger.error("powersave config.txt " + str(e))
        
    if "an" in content:
        try:
            for i in content["an"]:
                an.append(datetime.datetime.strptime(i,'%d.%m.%Y %H:%M')) # parse string to date
        except Exception as e:
            log2.logger.error("an: " + str(e))

    if "aus" in content:
        try:
            for i in content["aus"]:
                aus.append(datetime.datetime.strptime(i,'%d.%m.%Y %H:%M'))
        except Exception as e:
            log2.logger.error("aus: " + str(e))
            
            
    if "fps" in content:
        try:
            fps = int(content["fps"])
        except Exception as e:
            log2.logger.error("FPS config.txt Wert ist keine Zahl. Benutze Default Wert " + str(e))

    if "rotation" in content:
        try:
            rot = int(content["rotation"])
            if not(rot == 0 or rot == 90 or rot == 180 or rot == 270):
                rot = 0
                log2.logger.error("rotation ist ungleich 0/90/180/270! Setze Rotation auf 0. rot: " + str(rot))
        except Exception as e:
            log2.logger.error("rotation config.txt Wert ist keine Zahl. Benutze Default Wert" + str(e))
    
    
    if "resX" in content:
        try:
            resX = int(content["resX"])
        except Exception as e:
            log2.logger.error("resX config.txt Wert ist keine Zahl. Benutze Default Wert" + str(e))
    
    if "resY" in content:
        try:
            resY = int(content["resY"])
        except Exception as e:
            log2.logger.error("resY config.txt Wert ist keine Zahl. Benutze Default Wert" + str(e))   
            
    if "bitrate" in content:
        try:
            bitrate = int(content["bitrate"])
        except Exception as e:
            log2.logger.error("bitrate config.txt Wert ist keine Zahl. Benutze Default Wert" + str(e))   
    
    if "interval" in content:
        try:
            interval = int(content["interval"])
        except Exception as e:
            log2.logger.error("Interval config.txt Wert ist keine Zahl. Benutze Default Wert" + str(e))           

    if "stromPi" in content:
        try:
            if int(content["stromPi"]) == 1:
                stromPi = True
            else:
                stromPi = False
        except Exception as e:
            log2.logger.error("stromPi config.txt " + str(e))
        

    if "name" in content:
        try:
            kName = content["name"]
            
        except Exception as e:
            log2.logger.error("name config.txt " + str(e))

    if "sw" in content:
        try:
            if int(content["sw"]) == 1:
                bw = True
            else:
                bw = False
        except Exception as e:
            log2.logger.error("schwarzweiß config.txt " + str(e))
            
    if "verschlüsseln" in content:
        try:
            if int(content["verschlüsseln"]) == 1:
                encrypt = True
            else:
                encrypt = False
        except Exception as e:
            log2.logger.error("verschlüsseln config.txt " + str(e))
            
    if "empfänger" in content:
        try:
            receiver = content["empfänger"]
            
        except Exception as e:
            log2.logger.error("empfänger config.txt " + str(e))
            
    if "zero" in content:
        try:
            if int(content["zero"]) == 1:
                zero = True
            else:
                zero = False
        except Exception as e:
            log2.logger.error("zero config.txt " + str(e))
            
    if "sdcard" in content:
        try:
            if int(content["sdcard"]) == 1:
                sdcard = True
            else:
                sdcard = False
        except Exception as e:
            log2.logger.error("sdcard config.txt " + str(e))

    return an, aus, fps, rot, resX, resY, interval, powersave, ipAddress, stromPi, kName, bw, receiver, encrypt, zero, bitrate, sdcard