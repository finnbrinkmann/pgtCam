#!/usr/bin/python3


import datetime
import yaml
#import types

import picamera
import os
import serial
from time import sleep

import stromStatus
import syncClock
#from log import log as log
from strompi_config import writeSP
from readConfig import readConfig as readConfig
from readVoltage import getVersion as getVersion

import log2
import cam
import logging


try:
    version = "0.9.9.0"

    log2.logger.info("\n\n\t#################") 
    log2.logger.info(    "\t#     Start     #")
    log2.logger.info(    "\t#################")
    log2.logger.debug("Version: " + str(version))
    log2.logger.info("Zeit: " + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M')))
     
    
    # Super Default Values
    #Default values like camara name should be in the file /home/pi/defaultConfig.txt
    an = []
    aus = []
    fps = 7
    rot = 0
    resX = 704
    resY = 576
    interval = 15
    powersave = False
    ipAddress = ''
    stromPi = False
    kName = "KamX"
    bw = False
    encrypt = False
    receiver = ""
    zero = False # to determin which LED to turn off in powersave mode
    bitrate = 17000000
    
    bootedToRecord = True


    paths = ["/media/ntfs/","/media/vFat/","/media/exFat/"] # all possible mount points; check /etc/fstab
    path = ""

    try:
        camera = picamera.PiCamera()
        camera.resolution = (resX, resY) #4x3 size 
        camera.framerate = fps

        camera.start_preview(alpha = 240) #transparent preview
        camera.annotate_background = picamera.Color('black')
        camera.annotate_text = "Starte..."
    except Exception as e:
        log2.logger.error("konnte camera nicht starten. " + str(e))


    configFile = "/home/pi/defaultConfig.txt"
    an, aus, fps, rot, resX, resY, interval, powersave, ipAddress, stromPi, kName, bw, receiver, encrypt, zero, bitrate = readConfig(configFile, an, aus, fps, rot, resX, resY, interval, powersave, ipAddress, stromPi, kName, bw, receiver, encrypt, zero, bitrate)
    
    try:
        camera.rotation = rot
    except Exception as e:
        log2.logger.error("konnte camera nicht drehen. " + str(e))

    stickFound = False
    while not stickFound: #loopbreak until a stick is found
        
        for x in paths:
            
            if os.path.ismount(x):
                log2.logger.debug("Mountpunkt ist: " + str(x))
                path = x
                try:
                    usb_handler = logging.FileHandler(x + 'log.txt')
                    
                    usb_format = logging.Formatter('%(asctime)s|%(levelname)s\t%(message)s')
                    usb_handler.setFormatter(usb_format)
                    usb_handler.setLevel(logging.DEBUG)
                    log2.logger.addHandler(usb_handler)
                    log2.logger.debug("USB logger angelegt. " + x)
                except Exception as e:
                    log2.logger.error("Kann USB logger nicht initialisieren" + str(e))
                try:
                    configFile = str(x) + "config.txt"
                    an, aus, fps, rot, resX, resY, interval, powersave, ipAddress, stromPi, kName, bw, receiver, encrypt, zero, bitrate = readConfig(configFile, an, aus, fps, rot, resX, resY, interval, powersave, ipAddress,stromPi, kName, bw, receiver, encrypt, zero, bitrate)
                    
                except Exception as e:
                    log2.logger.warning("Kann Datei nicht lesen " + configFile + ". Datei vorhanden? " + str(e))
                    
                stickFound = True
        if not stickFound:
            camera.annotate_text = "KEIN USB-STICK GEFUNDEN! Version: " + str(version)
            sleep(5)
            log2.logger.info("Kein USB-Stick gefunden")
            #exit()
                
    #log again, if no usbstick was present
    log2.logger.debug("Version: " + str(version))
    log2.logger.info("Zeit: " + str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M')))
    
    log2.logger.debug("FPS: " + str(fps))
    log2.logger.debug("rot: " + str(rot))
    log2.logger.debug("resX: " + str(resX))
    log2.logger.debug("resY: " + str(resY))
    log2.logger.debug("bitrate: " + str(bitrate))
    log2.logger.debug("interval: " + str(interval))
    log2.logger.info("powersave: " + str(powersave))
    log2.logger.debug("graustufen: " + str(bw))
    log2.logger.debug("stromPi: " + str(stromPi))
    log2.logger.debug("Zero: " + str(zero))
    log2.logger.debug("Name: " + str(kName))
    log2.logger.debug("Empfänger: " + str(receiver))
    log2.logger.debug("Verschlüsseln: " + str(encrypt))


    if stromPi:
        log2.logger.debug("StromPi Firmware Version: " + str(getVersion()))
    
    log2.logger.info("USB-Stick gefunden")
    try:
        camera.annotate_text = "USB-Stick gefunden"
    except Exception as e:
        log2.logger.error("Camera fehler. " + str(e))
        


    try:
        #def serial connection to communicate with the strom pi
        serial_port = serial.Serial()
        serial_port.baudrate = 38400
        #serial_port.port = '/dev/serial0'
        serial_port.port = '/dev/ttyAMA0'
        serial_port.timeout = 1
        serial_port.bytesize = 8
        serial_port.stopbits = 1
        serial_port.parity = serial.PARITY_NONE
        breakS = 0.1
        breakL = 0.2
    except Exception as e:
        log2.logger.error("Serial init Fehlerhaft. " + str(e))


    nextPoweroff = datetime.datetime.strptime('Jun 1 2080  1:33PM', '%b %d %Y %I:%M%p') # max date in future

    if stromPi:
        log2.logger.debug("StromPi soll vorhanden sein")
        try:#Uhren Synconisieren
            syncClock.syncClock()
        except Exception as e:
            log2.logger.error("SPi Uhr konnte nicht Sync werden. " + str(e))


        if serial_port.isOpen(): serial_port.close()
        
        try:
            serial_port.open()
        except Exception as e:
            log2.logger.error("Fehler in der seriellen Kommunikation. " + str(e))

        #arrange items in the correct order
        an.sort()
        aus.sort()
        an.reverse()
        aus.reverse()

        
        if len(an) > 0:
            bootedToRecord = False
        
        for i in an[::-1]: #loop in reverse order to del items correctly
            
            if i > datetime.datetime.now() + datetime.timedelta(minutes=5):
                log2.logger.info("Datum liegt in der Zukunft " + str (i))
            else:
                log2.logger.info("Datum liegt in der Vergangenheit und wird ignoriert! " + str (i))
                an.remove(i)
                bootedToRecord = True # if there are some dates in the past, we assume that we started to record


        for i in aus[::-1]: #loop in reverse order to del items correctly
            if i > datetime.datetime.now():
                log2.logger.info("Datum in Zukunft " + str (i))
            else:
                log2.logger.info("Datum in Vergangenheit - ignoriert " + str (i))
                aus.remove(i)


        if an: # if an has still items (dates in the future)
            
            try:
                log2.logger.info("Programm StromPi")
                
                nextTime = an.pop()# get next date coming
                
                nextTime = nextTime - datetime.timedelta(minutes=5)# substract 5 min to make sure RPi is booted and ready when recording should start.
                
                log2.logger.info("Nächster Start: " + str(nextTime))
                
                #sp3_alarm_enable = 1
                sp3_alarm_min = nextTime.strftime("%M")
                sp3_alarm_hour = nextTime.strftime("%H")
                sp3_alarm_day = nextTime.strftime("%d")
                sp3_alarm_month = nextTime.strftime("%m")
                
                writeSP(sp3_alarm_month,sp3_alarm_day,sp3_alarm_hour,sp3_alarm_min) # write next start time to the RPi
                
            except Exception as e:
                log2.logger.error("Error: Konnte nächsten Anschaltzeitpunkt nicht konfigurieren. Empfehle neustart. Notaufzeichnung start" + str(e))           

        else:
            log2.logger.info("Keine weiteren Einschaltzeitpunkte!")
            
        if aus: # if has items
            log2.logger.info("Es sind Ausschaltzeiten programmiert")
            #we dont use the shutoff tool of the strompi, but shutdown by ourself
        else:
            log2.logger.info("Keine weiteren Ausschaltzeitpunkte!")
            

            
        if aus:
            #get time of next shutdown
            nextPoweroff = aus.pop()
    
    try:
        camera.close() #close preview camera
    except Exception as e:
        log2.logger.error("Konnte Kamera Obj nicht schließen " + str(e))


    if bootedToRecord: # record for 15 min to set up the camera and then poweroff

        try:
            cam.recVideo(nextPoweroff, fps, resX, resY, interval, powersave, rot, str(ipAddress), stromPi, kName, path, bw, receiver, encrypt, zero, bitrate) #record video until next poweroff time is reached
        except Exception as e:
            log2.logger.error("Schwerer Fehler! Konnte Aufzeichnung nicht starten!" + str(e))
            # this might happen if the usb is lost
            
            try:
                sleep(10)
                nextPoweroff = datetime.datetime.strptime('Jun 1 2080  1:33PM', '%b %d %Y %I:%M%p') # max date in future
                cam.recVideo(nextPoweroff, 7, 400, 300, 15, False, rot, "", False, kName, "/home/pi/rec/", True , None, False, False, 10000) #record to SD Card in
            except Exception as e:
                log2.logger.error("Schwerer Fehler! Notfallaufzeichung auf die SD-Karte fehlgeschlagen!" + str(e))
            
            raise # fire main exception to reboot

    else:
        try:
            #record short preview
            nextPoweroff = datetime.datetime.now() + datetime.timedelta(minutes=15)
            log2.logger.info("Keine Startzeiten in der Vergangenheit. 15min Preview, danach PowerOff!")
            cam.recVideo(nextPoweroff, fps, resX, resY, interval, powersave, rot, str(ipAddress), stromPi, kName, path, bw, receiver, encrypt, zero, bitrate)

        except Exception as e:
            log2.logger.error("Schwerer Fehler! Power off nicht Erfolgreich! Programmierung fehlgeschlagen! " + str(e))
            raise


    #shutdown
    log2.logger.info("shutting down now")
    
    if stromPi: # if stromPi is used, shut it down first
        try:
            serial_port.write(str.encode('poweroff')) #
            sleep(breakS)
            serial_port.write(str.encode('\x0D'))
            sleep(breakL)
        except Exception as e:
            log2.logger.error("StromPi hat kein Poweroff signal erhalten " + str(e))
            
    os.system('sudo shutdown +0')

#if everything is broken
except Exception as e:
    print(e)
    log2.logger.error("Unerwarteter Ausnahmefehler! KEINE Aufzeichnung! " + str(e))
    log2.logger.error("Unerwarteter Ausnahmefehler! KEINE Aufzeichnung! " + str(e))
    log2.logger.error("Unerwarteter Ausnahmefehler! KEINE Aufzeichnung! " + str(e))

    try:
        camera.annotate_background = picamera.Color('red')   
        camera.annotate_text = "ERROR! KEINE AUFZEICHNUNG! " + str(e)
    except Exception as e:
        print(e)
        
    try:
        camera = picamera.PiCamera() # hardcoded failsafe
        camera.resolution = (640, 480) #4x3 size 
        camera.framerate = 10
        
        camera.start_preview(alpha = 200) #transparent preview

        camera.annotate_background = picamera.Color('red')   
        camera.annotate_text = "ERROR! KEINE AUFZEICHNUNG! " + str(e)
    except Exception as e:
        print(e)


    log2.logger.critical("Starte in 60s NEU!!!!! ")
    log2.logger.critical("Starte in 60s NEU!!!!! ")
    log2.logger.critical("Starte in 60s NEU!!!!! ")
    
    #last hope: reboot
    sleep(60) #60s to ssh and kill the process to prevent reboot loop
    os.system('sudo reboot')
    
exit()


