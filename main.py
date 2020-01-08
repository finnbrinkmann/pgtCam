#!/usr/bin/python3


import datetime
import yaml
#import types
import socket
import picamera
import os
import serial
from time import sleep

import stromStatus
import syncClock
from log import log as log
from strompi_config import writeSP
from readConfig import readConfig as readConfig

import cam




try:


    log("\n\n#################") 
    log(    "#     Start     #")
    log(    "#################")

    # Super Default Values
    an = []
    aus = []
    fps = 10
    rot = 0
    resX = 704
    resY = 576
    interval = 15
    powersave = False
    ipAddress = ''



    try:
        camera = picamera.PiCamera()
        camera.resolution = (640, 480) #4x3 size 
        camera.framerate = 10

        camera.start_preview(alpha = 240) #transparent preview
        camera.annotate_background = picamera.Color('black')
        camera.annotate_text = "Starte..."
    except Exception as e:
        log("ERROR: konnte camera nicht starten. " + str(e))

    try:#Uhren Synconisieren
        syncClock.syncClock()
    except Exception as e:
        log("ERROR: SPi Uhr konnte nicht Sync werden. " + str(e))

    configFile = "/home/pi/defaultConfig.txt"
    an, aus, fps, rot, resX, resY, interval, powersave, ipAddress = readConfig(configFile, an, aus, fps, rot, resX, resY, interval, powersave, ipAddress)

    while True: #loopbreak until a stick is found
        
        if os.path.ismount("/media/stick/"):
            try:
                configFile = "/media/stick/config.txt"
                an, aus, fps, rot, resX, resY, interval, powersave, ipAddress = readConfig(configFile, an, aus, fps, rot, resX, resY, interval, powersave, ipAddress)
                
            except Exception as e:
                log ("ERROR: Kann Datei nicht lesen /media/stick/config.txt. Datei vorhanden? " + str(e))
                
            break
        else:
            camera.annotate_text = "KEIN USB-STICK GEFUNDEN"
            sleep(5)
            log ("INFO: Kein USB-Stick gefunden")
            #exit()
            
            
            
    
    log ("INFO: USB-Stick gefunden")


    #def serial connection to communicate with the strom pi

    serial_port = serial.Serial()
    serial_port.baudrate = 38400
    #serial_port.port = '/dev/serial0'
    serial_port.port = '/dev/ttyAMA0'
    serial_port.timeout = 1
    serial_port.bytesize = 8
    serial_port.stopbits = 1
    serial_port.parity = serial.PARITY_NONE

    if serial_port.isOpen(): serial_port.close()
    
    try:
        serial_port.open()
    except Exception as e:
        log("ERROR: Fehler in der seriellen Kommunikation. " + str(e))

    breakS = 0.1
    breakL = 0.2

    nextPoweroff = datetime.datetime.strptime('Jun 1 2080  1:33PM', '%b %d %Y %I:%M%p') # max date in future


            



    #arrange items in the correct order
    an.sort()
    aus.sort()
    an.reverse()
    aus.reverse()

    for i in an[::-1]: #loop in reverse order to del items correctly
        if i > datetime.datetime.now() + datetime.timedelta(minutes=5):
            log("INFO: Datum liegt in der Zukunft " + str (i))
        else:
            log("INFO: Datum liegt in der Vergangenheit und wird ignoriert! " + str (i))
            an.remove(i)
            bootedToRecord = True # if there are some dates in the past, we assume that we started to record


    for i in aus[::-1]: #loop in reverse order to del items correctly
        if i > datetime.datetime.now():
            log("INFO: Datum in Zukunft " + str (i))
        else:
            log("INFO: Datum in Vergangenheit - ignoriert " + str (i))
            aus.remove(i)


    if an: # if an has still items (dates in the future)
        
        try:
            log ("INFO: Programm StromPi")
            
            nextTime = an.pop()# get next date coming
            
            nextTime = nextTime - datetime.timedelta(minutes=5)# substract 5 min to make sure RPi is booted and ready when recording should start.
            
            log ("INFO: Nächster Start: " + str(nextTime))
            
            #sp3_alarm_enable = 1
            sp3_alarm_min = nextTime.strftime("%M")
            sp3_alarm_hour = nextTime.strftime("%H")
            sp3_alarm_day = nextTime.strftime("%d")
            sp3_alarm_month = nextTime.strftime("%m")
            
            writeSP(sp3_alarm_month,sp3_alarm_day,sp3_alarm_hour,sp3_alarm_min) # write next start time to the RPi
            
        except Exception as e:
            log("Error: Konnte nächsten Anschaltzeitpunkt nicht konfigurieren. Empfehle neustart. Notaufzeichnung start" + str(e))           

    else:
        log ("INFO: Keine weiteren Einschaltzeitpunkte!")
        
    if aus: # if has items
        log ("INFO: Es sind Ausschaltzeiten programmiert")
        #we dont use the shutoff tool of the strompi, but shutdown by ourself
    else:
        log ("INFO: Keine weiteren Ausschaltzeitpunkte!")
        
    if not bootedToRecord:

        try:
            
            nextPoweroff = datetime.datetime.now() + datetime.timedelta(minutes=15)
            log("INFO: Keine Startzeiten in der Vergangenheit. 15min Preview, danach PowerOff!")
            cam.recVideo(nextPoweroff, fps, resX, resY, interval, 180, str(ipAddress))
            serial_port.write(str.encode('poweroff'))
            sleep(breakS)
            serial_port.write(str.encode('\x0D'))
            sleep(breakL)
            os.system('sudo shutdown +0')
            exit()
        except Exception as e:
            log("Error: Schwerer Fehler! Power off nicht Erfolgreich! Programmierung fehlgeschlagen! " + str(e))
        
        
    if aus:
        #get time of next shutdown
        nextPoweroff = aus.pop()
    
    try:
        camera.close()
    except Exception as e:
        log("Error: StromPi hat kein Poweroff signal erhalten " + str(e))
        
    try:
        cam.recVideo(nextPoweroff, fps, resX, resY, interval, powersave, 180, str(ipAddress)) #record video until next poweroff time is reached
    except Exception as e:
        log("Error: Schwerer Fehler! Konnte Aufzeichnung nicht starten!" + str(e))
        raise
        

    #shutdown
    log("END: shutting down now")
    try:
        serial_port.write(str.encode('poweroff'))
        sleep(breakS)
        serial_port.write(str.encode('\x0D'))
        sleep(breakL)
    except Exception as e:
        log("Error: StromPi hat kein Poweroff signal erhalten " + str(e))
        
    os.system('sudo shutdown +0')
    
except Exception as e:
    print(e)
    log("ERROR: Unerwarteter Ausnahmefehler! KEINE Aufzeichnung! " + str(e))
    log("ERROR: Unerwarteter Ausnahmefehler! KEINE Aufzeichnung! " + str(e))
    log("ERROR: Unerwarteter Ausnahmefehler! KEINE Aufzeichnung! " + str(e))
    
    try:
        camera = picamera.PiCamera() # hardcoded failsafe
        camera.resolution = (640, 480) #4x3 size 
        camera.framerate = 10
        
        camera.start_preview(alpha = 200) #transparent preview

        camera.annotate_background = picamera.Color('red')   
        camera.annotate_text = "ERROR! KEINE AUFZEICHNUNG! " + str(e)
    except Exception as e:
        print(e)
        
    log("Starte in 60s NEU!!!!! ")
    log("Starte in 60s NEU!!!!! ")
    log("Starte in 60s NEU!!!!! ")
    
    sleep(60)
    os.system('sudo reboot')
    
exit()


