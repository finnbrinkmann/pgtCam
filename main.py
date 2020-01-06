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

import cam

try:


    log("\n\n#################") 
    log(    "#     Start     #")
    log(    "#################")


    try:
        camera = picamera.PiCamera()
        camera.resolution = (640, 480) #4x3 size 
        camera.framerate = 10

        camera.start_preview(alpha = 240) #transparent preview
        camera.annotate_background = picamera.Color('black')
    except Exception as e:
        log("ERROR: konnte camera nicht starten. " + str(e))

    try:#Uhren Synconisieren
        syncClock.syncClock()
    except Exception as e:
        log("ERROR: SPi Uhr konnte nicht Sync werden. " + str(e))


    while True: #loopbreak until a stick is found
        
        if os.path.ismount("/media/stick/"):
            try:
                configFile = open("/media/stick/config.txt", "r")
                log ("INFO: /media/stick/config.txt geöffnet")
                
            except Exception as e:
                log ("ERROR: Kann Datei nicht lesen /media/stick/config.txt. Datei vorhanden? " + str(e))
                
            break
        else:
            camera.annotate_text = "KEIN USB-STICK GEFUNDEN"
            sleep(5)
            log ("INFO: Kein USB-Stick gefunden")
            #exit()

    camera.annotate_text = "Starte..."
    
    log ("INFO: USB-Stick gefunden")
    try:
        content = yaml.load(configFile, Loader=yaml.FullLoader) # read config file in yaml format
    except Exception as e:
        log("ERROR: Fehler in lesen der Config Datei! " + str(e))
        content = {}


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
        log("ERROR: Error: Fehler in der seriellen Kommunikation. " + str(e))

    breakS = 0.1
    breakL = 0.2

    nextPoweroff = datetime.datetime.strptime('Jun 1 2080  1:33PM', '%b %d %Y %I:%M%p') # max date in future

    #log config file
    if not content:
        try:
            for key, value in content.items():
                log ('\t' + str(key) + " : " + str(value))
        except Exception as e:
            log("Error: Lesen von config.txt fehlerhaft " + str(e))
            
    # Default Values
    an = []
    aus = []
    fps =  24
    resX = 704
    resY = 576
    interval = 15
    powersave = False
    ipAddress = ''

    # check if parameters are set in config file. Problem is, that we have to reboot the RPi in order wifi changes to become active. 
    if "wlan" in content:
        try:
            wlan = str(content["wlan"])
            if content["wlan-pw"]: #need wifi network and password (pw in plain text)

                try:
                    wlanPW = str(content["wlan-pw"])
                except Exception as e:
                    log("Error: WLAN Passwort nicht erkannt. " + str(e))
                try:
                    os.system('sudo sed -i \'s/ssid=".*"/ssid="' + wlan + '"/g\' /etc/wpa_supplicant/wpa_supplicant.conf')# replace string in wifi config file
                    os.system('sudo sed -i \'s/psk=".*"/psk="' + wlanPW + '"/g\' /etc/wpa_supplicant/wpa_supplicant.conf')
                    os.system('sudo sed -i \'s/#*dtoverlay=pi3-disable-wifi/#dtoverlay=pi3-disable-wifi/g\' /etc/wpa_supplicant/wpa_supplicant.conf')
                    log("INFO: WLAN + Passwort eingetragen: " + wlan) 
                    
                    wifiActive = os.system('ifconfig wlan0') # get wifi info if it is active (seems not to work that good)
                    log("INFO: WiFi-Status: " + str(wifiActive))
                    
                    try:#insteat ping googles DNS server to see if we have internet connection
                        soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        soc.connect(("8.8.8.8", 80))
                        ipAddress = soc.getsockname()[0]
                        log("INFO: IP-Address: " + str(ipAddress))
                        soc.close()
                    except Exception as e:
                        log("WARNING: WLAN noch inaktiv. Reboot " + str(e))
                    if wifiActive > 0:
                        log("INFO: WLAN wurde aktiviert. Neustart wird durchgeführt")#if wifi  tag is set but wifi is not active, we have to assume that wifi was set right now and we have to reboot. (this is dangerous since we might end up in a reboot loop)
                        #os.system('sudo reboot')
                    
                    
                except Exception as e:
                    log("ERROR: WLAN Einstellungen wurden nicht übernommen. " + str(e))
                
        except Exception as e:
            log("Error: WLAN Namen nicht erkannt. " + str(e))


    else:
        try: # TODO try if wifi is active, if so reboot 
            os.system('sudo sed -i \'s/ssid=".*"/ssid=""/g\' /etc/wpa_supplicant/wpa_supplicant.conf') # if wifi tag is not set. remove wifi data from config file
            os.system('sudo sed -i \'s/psk=".*"/psk=""/g\' /etc/wpa_supplicant/wpa_supplicant.conf')
            os.system('sudo sed -i \'s/#*dtoverlay=pi3-disable-wifi/dtoverlay=pi3-disable-wifi/g\' /etc/wpa_supplicant/wpa_supplicant.conf')
            log("INFO: WLAN deaktiviert")
        except Exception as e:
            log("WARNING: WLAN konnte nicht zurückgesetzt werden und ist möglicherweise aktivert. " + str(e))
     

    if "powersave" in content:
        
        powersave = True
        log("Powersave ist aktiviert")
     
        
    if "an" in content:
        bootedToRecord = False
        for i in content["an"]:
            an.append(datetime.datetime.strptime(i,'%d.%m.%Y %H:%M')) # parse string to date
    else:
        bootedToRecord = True #if there are no dates defined to start the RPi, we go to record immediately

    if "aus" in content:
        for i in content["aus"]:
            aus.append(datetime.datetime.strptime(i,'%d.%m.%Y %H:%M'))
            
    if "fps" in content:
        try:
            fps = int(content["fps"])
        except ValueError as e:
            log("Error: FPS config.txt Wert ist keine Zahl. Benutze Default Wert " + str(e))

    if "rotation" in content:
        try:
            rot = int(content["rotation"])
            if not(rot == 0 or rot == 90 or rot == 180 or rot == 270):
                rot = 0
            log("Error: rotation ist ungleich 0/90/180/270! Setze Rotation auf 0")
        except ValueError as e:
            log("Error: rotation config.txt Wert ist keine Zahl. Benutze Default Wert" + str(e))
    
    
    if "resX" in content:
        try:
            resX = int(content["resX"])
        except ValueError as e:
            log("Error: resX config.txt Wert ist keine Zahl. Benutze Default Wert" + str(e))
    
    if "resY" in content:
        try:
            resY = int(content["resY"])
        except ValueError as e:
            log("Error: resY config.txt Wert ist keine Zahl. Benutze Default Wert" + str(e))   
    
    if "interval" in content:
        try:
            interval = int(content["interval"])
        except ValueError as e:
            log("Error: Interval config.txt Wert ist keine Zahl. Benutze Default Wert" + str(e))           

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


