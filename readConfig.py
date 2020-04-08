import datetime
import yaml
#import types
import os
from log import log as log
import socket
from time import sleep
import log2

def readConfig(filename, an, aus, fps, rot, resX, resY, interval, powersave, ipAddress, stromPi, kName, bw, receiver, encrypt, zero, bitrate):


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
    if "wlan" in content:
        try:
            wlan = str(content["wlan"])
            if content["wlan-pw"]: #need wifi network and password (pw in plain text)

                try:
                    wlanPW = str(content["wlan-pw"])
                except Exception as e:
                    log2.logger.error("WLAN Passwort nicht erkannt. " + str(e))
                try:
                    os.system('sudo sed -i \'s/ssid=".*"/ssid="' + wlan + '"/g\' /etc/wpa_supplicant/wpa_supplicant.conf')# replace string in wifi config file
                    os.system('sudo sed -i \'s/psk=".*"/psk="' + wlanPW + '"/g\' /etc/wpa_supplicant/wpa_supplicant.conf')
                    os.system('sudo sed -i \'s/#*dtoverlay=pi3-disable-wifi/#dtoverlay=pi3-disable-wifi/g\' /etc/wpa_supplicant/wpa_supplicant.conf')
                    log2.logger.debug("WLAN + Passwort eingetragen: " + wlan) 
                    
                    wifiActive = os.system('ifconfig wlan0') # get wifi info if it is active (seems not to work that good)
                    log2.logger.debug("WiFi-Status: " + str(wifiActive))
                    
                    try:#insteat ping googles DNS server to see if we have internet connection
                        sleep(30)# sleep some time for the os to get wifi working
                        soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        soc.connect(("8.8.8.8", 80))# try to connect to googles dns server to check for internet access
                        ipAddress = soc.getsockname()[0]
                        log2.logger.info("IP-Address: " + str(ipAddress))
                        soc.close()
                    except Exception as e:
                        log2.logger.warning("WLAN noch inaktiv." + str(e))
                    if wifiActive > 0:
                        log2.logger.info("WLAN wurde aktiviert.Neustart könnte erforderlich sein")#if wifi  tag is set but wifi is not active, we have to assume that wifi was set right now and we have to reboot. (this is dangerous since we might end up in a reboot loop)
                        #os.system('sudo reboot')
                    
                    
                except Exception as e:
                    log2.logger.error("WLAN Einstellungen wurden nicht übernommen. " + str(e))
                
        except Exception as e:
            log2.logger.error("WLAN Namen nicht erkannt. " + str(e))


    else:
        try: # TODO try if wifi is active, if so reboot 
            os.system('sudo sed -i \'s/ssid=".*"/ssid=""/g\' /etc/wpa_supplicant/wpa_supplicant.conf') # if wifi tag is not set. remove wifi data from config file
            os.system('sudo sed -i \'s/psk=".*"/psk=""/g\' /etc/wpa_supplicant/wpa_supplicant.conf')
            os.system('sudo sed -i \'s/#*dtoverlay=pi3-disable-wifi/dtoverlay=pi3-disable-wifi/g\' /etc/wpa_supplicant/wpa_supplicant.conf')
            log2.logger.info("WLAN deaktiviert")
        except Exception as e:
            log2.logger.warning("WLAN konnte nicht zurückgesetzt werden und ist möglicherweise aktivert. " + str(e))


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

    return an, aus, fps, rot, resX, resY, interval, powersave, ipAddress, stromPi, kName, bw, receiver, encrypt, zero, bitrate