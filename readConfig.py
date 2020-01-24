import datetime
import yaml
#import types
import os
from log import log as log


def readConfig(filename, an, aus, fps, rot, resX, resY, interval, powersave, ipAddress, stromPi, kName, bw, receiver, encrypt):


    configFile = ""
    content = {}


    try:
        configFile = open(filename, "r")
        log ("INFO: " + str (filename) + " geöffnet")
        
    except Exception as e:
        log ("WARNING: Kann Datei nicht lesen " + filename + ". Datei vorhanden? " + str(e))
    try:
        content = yaml.load(configFile, Loader=yaml.FullLoader) # read config file in yaml format
    except Exception as e:
        log("ERROR: Fehler in lesen der Config Datei! " + str(e))
        raise


    #log config file
    if content:
        try:
            for key, value in content.items():
                log ('\t' + str(key) + " : " + str(value))
        except Exception as e:
            log("ERROR: Lesen von config.txt fehlerhaft " + str(e))


    # check if parameters are set in config file. Problem is, that we have to reboot the RPi in order wifi changes to become active. 
    if "wlan" in content:
        try:
            wlan = str(content["wlan"])
            if content["wlan-pw"]: #need wifi network and password (pw in plain text)

                try:
                    wlanPW = str(content["wlan-pw"])
                except Exception as e:
                    log("ERROR: WLAN Passwort nicht erkannt. " + str(e))
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
                        log("WARNING: WLAN noch inaktiv." + str(e))
                    if wifiActive > 0:
                        log("INFO: WLAN wurde aktiviert.Neustart könnte erforderlich sein")#if wifi  tag is set but wifi is not active, we have to assume that wifi was set right now and we have to reboot. (this is dangerous since we might end up in a reboot loop)
                        #os.system('sudo reboot')
                    
                    
                except Exception as e:
                    log("ERROR: WLAN Einstellungen wurden nicht übernommen. " + str(e))
                
        except Exception as e:
            log("ERROR: WLAN Namen nicht erkannt. " + str(e))


    else:
        try: # TODO try if wifi is active, if so reboot 
            os.system('sudo sed -i \'s/ssid=".*"/ssid=""/g\' /etc/wpa_supplicant/wpa_supplicant.conf') # if wifi tag is not set. remove wifi data from config file
            os.system('sudo sed -i \'s/psk=".*"/psk=""/g\' /etc/wpa_supplicant/wpa_supplicant.conf')
            os.system('sudo sed -i \'s/#*dtoverlay=pi3-disable-wifi/dtoverlay=pi3-disable-wifi/g\' /etc/wpa_supplicant/wpa_supplicant.conf')
            log("INFO: WLAN deaktiviert")
        except Exception as e:
            log("WARNING: WLAN konnte nicht zurückgesetzt werden und ist möglicherweise aktivert. " + str(e))


    if "powersave" in content:
        try:
            if int(content["powersave"]) == 1:
                powersave = True
        except Exception as e:
            log("ERROR: powersave config.txt " + str(e))
        
    if "an" in content:
        for i in content["an"]:
            an.append(datetime.datetime.strptime(i,'%d.%m.%Y %H:%M')) # parse string to date


    if "aus" in content:
        for i in content["aus"]:
            aus.append(datetime.datetime.strptime(i,'%d.%m.%Y %H:%M'))
            
    if "fps" in content:
        try:
            fps = int(content["fps"])
        except ValueERROR as e:
            log("ERROR: FPS config.txt Wert ist keine Zahl. Benutze Default Wert " + str(e))

    if "rotation" in content:
        try:
            rot = int(content["rotation"])
            if not(rot == 0 or rot == 90 or rot == 180 or rot == 270):
                rot = 0
                log("ERROR: rotation ist ungleich 0/90/180/270! Setze Rotation auf 0. rot: " + str(rot))
        except ValueERROR as e:
            log("ERROR: rotation config.txt Wert ist keine Zahl. Benutze Default Wert" + str(e))
    
    
    if "resX" in content:
        try:
            resX = int(content["resX"])
        except ValueERROR as e:
            log("ERROR: resX config.txt Wert ist keine Zahl. Benutze Default Wert" + str(e))
    
    if "resY" in content:
        try:
            resY = int(content["resY"])
        except ValueERROR as e:
            log("ERROR: resY config.txt Wert ist keine Zahl. Benutze Default Wert" + str(e))   
    
    if "interval" in content:
        try:
            interval = int(content["interval"])
        except ValueERROR as e:
            log("ERROR: Interval config.txt Wert ist keine Zahl. Benutze Default Wert" + str(e))           

    if "stromPi" in content:
        try:
            if int(content["stromPi"]) == 1:
                stromPi = True
        except Exception as e:
            log("ERROR: stromPi config.txt " + str(e))
        

    if "name" in content:
        try:
            kName = content["name"]
            
        except Exception as e:
            log("ERROR: name config.txt " + str(e))

    if "sw" in content:
        try:
            if int(content["sw"]) == 1:
                bw = True
        except Exception as e:
            log("ERROR: schwarzweiß config.txt " + str(e))
            
    if "verschlüsseln" in content:
        try:
            if int(content["verschlüsseln"]) == 1:
                encrypt = True
        except Exception as e:
            log("ERROR: verschlüsseln config.txt " + str(e))
            
    if "empfänger" in content:
        try:
            receiver = content["empfänger"]
            
        except Exception as e:
            log("ERROR: empfänger config.txt " + str(e))
            
            

    return an, aus, fps, rot, resX, resY, interval, powersave, ipAddress, stromPi, kName, bw, receiver, encrypt