#PYTHON3 !!!

import time
import picamera 
import datetime as dt
#import subprocess #system calls
import os
import subprocess
from log import log as log
from readVoltage import logBatLevel as logBat


def recVideo(powerOffTime, fps, resX, resY, intervalLength, powersave, rot, msg, stromPi, kName, path, bw, receiver, encrypt):

    
    
    #camera is activated
    camera = picamera.PiCamera()
    
    try:
        camera.rotation = rot
        camera.resolution = (resX, resY) #4x3 size 
        camera.framerate = fps
        
        camera.start_preview(alpha = 250) #transparent preview
        camera.annotate_background = picamera.Color('black')
        
        #resize annotation text size to video resY
        annotateTextSize = int(resY / 18)  # resY / 18 results in 576/32 = 18 defaultvideo size / default text size = default ratio. Use the same ratio for textsize for different ressotutions 
        if annotateTextSize < 6: #cant be smaller
            camera.annotate_text_size = 6 
        elif annotateTextSize > 160:#cant be bigger max:160 
            camera.annotate_text_size = 160
        else:
            camera.annotate_text_size = annotateTextSize #default: 32
            
        
        if bw: # black/white (graysale)
            camera.color_effects =(128,128)
    
    except Exception as e:
        log ("ERROR: Cameraparameter fehlerhaft. " + str(e))
    
    
    log ("INFO: Aufzeichnung wird vorbereitet.")
    batVoltageString = ""
    #log (str(stromPi))
    
    if stromPi:
        camera.annotate_text = "Abfrage der Batteriespannung..."
        batVoltage = logBat()
        batVoltageString = str(batVoltage) + "V"
    
    camera.annotate_text = "Aufzeichnung wird vorbereitet..."
    
    outputName = ""
    oldOutputName = ""

    try:
        diskFree = int(os.popen("df --output=avail /dev/sda1 |tail -n 1").read().strip()) #get harddisk free space. 
        diskUsed = int(os.popen("df --output=used /dev/sda1 |tail -n 1").read().strip()) #get harddisk used space
        usage = str(int(diskFree / (diskFree + diskUsed) *100 )) + "%"
        
    except Exception as e:

        log ("ERROR: Fehler beim Abfragen vom USB-Speicherplatz. " + str(e))
        usage = 'USB-FEHLER'


    #wait for next 15 min interval
    tm = dt.datetime.now()


    #tm = tm - dt.timedelta(minutes=(tm.minute % 15)-30, seconds=tm.second, microseconds=tm.microsecond) # calc time of next 0/15/30/45min (and add additional 15min)
    tm = tm - dt.timedelta(minutes=(tm.minute % 15)-15, seconds=tm.second, microseconds=tm.microsecond) #for debug, to speed up dev time

    try:
        path = path + kName + '/'
        os.makedirs(path, exist_ok=True) # create folder if does not exist
        outputName = path + dt.datetime.now().strftime('%Y-%m-%d_%H-%M') + 'preview'
    except Exception as e:
        log("ERROR: Konnte Ordner nicht anlegen. USB-Stick fehlerhaft? " + str(e))
    
    try:
        camera.start_recording(outputName  + '.h264')
    except Exception as e:
        print ("ERROR: Aufnahmefehler. USB-Stick noch vorhanden?!" + str(e))
        
        
    #loop until next 00/15/30/45min is reached
    while True:
        time.sleep(1)
        fileSize = os.path.getsize(outputName + '.h264') % 100 #to limit output to 2 numbers
        #log("filesize = " + str(fileSize))
        annotation = dt.datetime.now().strftime('%H:%M:%S %d.%m.%Y ') + " " + kName + ' ' + usage + ' ' + batVoltageString + str(fileSize) + ' ' + msg
        camera.annotate_text = annotation
        if tm < dt.datetime.now(): 
            break

    end = time.time() # seconds since 1970

    log ("INFO: Starte die Aufnahme")
    oldOutputName = outputName #remember old file in order to encode and delete
    outputName = path + dt.datetime.now().strftime('%Y-%m-%d_%H-%M')
    camera.split_recording(outputName  + '.h264') # create a new file every intervalLength (15) min
    
    #try:
    #    subprocess.Popen(["MP4Box","-fps", str(fps),"-add",oldOutputName + '.h264', oldOutputName + '.mp4']) # convert h264 to mp4 format. 
    #    log("INFO: " + oldOutputName + ".mp4 komplett." +  dt.datetime.now().strftime('%Y-%m-%d_%H-%M'))
    #except Exception as e: 
    #    log("ERROR: Codierung fehlgeschlagen! " + oldOutputName + " " + str(e))
    #    oldOutputName = "" # prevent deletion of file
        
        
    if encrypt:
        try:
            cmdEncode = "MP4Box" + " -fps " + str(fps) +" -add " + oldOutputName + ".h264 " + oldOutputName + '.mp4'
            cmdEncrypt = "gpg" + " --output " + oldOutputName + '.mp4.gpg' + " --recipient " + receiver + " --encrypt " + oldOutputName + '.mp4'
            os.system(cmdEncode + ";" + cmdEncrypt)
            #subprocess.Popen(["MP4Box","-fps", str(fps),"-add",oldOutputName+ '.h264', oldOutputName+ '.mp4']) # convert h264 to mp4 format
            #log("INFO: " + oldOutputName + ".mp4 komplett." +  dt.datetime.now().strftime('%Y-%m-%d_%H-%M'))
            #subprocess.Popen(["gpg","--output", oldOutputName+ '.gpg',"--recipient", receiver, "--encrypt", oldOutputName+ '.mp4']) # convert h264 to mp4 format
            log("INFO: " + oldOutputName + ".gpg komplett." +  dt.datetime.now().strftime('%Y-%m-%d_%H-%M'))
        except Exception as e: 
            log("ERROR: Verschlüsselung fehlgeschlagen! " + oldOutputName + " " + str(e))
            oldOutputName = ""
    else:
        try:
            subprocess.Popen(["MP4Box","-fps", str(fps),"-add",oldOutputName+ '.h264', oldOutputName+ '.mp4']) # convert h264 to mp4 format
            log("INFO: " + oldOutputName + ".mp4 komplett." +  dt.datetime.now().strftime('%Y-%m-%d_%H-%M'))
        except Exception as e: 
            log("ERROR: Codierung fehlgeschlagen! " + oldOutputName + " " + str(e))
            oldOutputName = ""        


    if powersave: # activate powersave mode if set in conig txt. 
        try:
            os.system('echo 0 | sudo tee /sys/class/leds/led0/brightness') #deactivate green RPi onboard LED
            os.system('echo 0 | sudo tee /sys/class/leds/led1/brightness') #deactivate green RPi onboard LED
            os.system('/usr/bin/tvservice -o') # deactivate display ports
            log("INFO: POWERSAVE aktiviert")
        except Exception as e:
            log("WARNING: PowerSave Fehler. " + str(e))

    #camera.wait_recording(1)
    log("INFO: Aufzeichnen läuft bis: " + str(powerOffTime))

############### Record loop
    while dt.datetime.now() < powerOffTime: # until time off date is reached

        if stromPi:
            batVoltage = logBat() # log the Battery voltage #braucht das sehr lange wenn kein strom pi angeschlossen ist?!
            batVoltageString = str(batVoltage) + "V"
            
        end = end + intervalLength * 60 # add 15 min * 60 sec/min
        
        
        try:
            diskFree = int(os.popen("df --output=avail /dev/sda1 |tail -n 1").read().strip()) #get harddisk free space. 
            diskUsed = int(os.popen("df --output=used /dev/sda1 |tail -n 1").read().strip()) #get harddisk used space
            usage = str(int(diskFree / (diskFree + diskUsed) *100 )) + "%"
            
        except Exception as e:
            log("WARNING: Fehler in Speicherplatzabfrage" + str(e))
            usage = "?%"
            #raise
            #a reboot might be necessary
            
        while time.time() < end : # while 15min (or intervall length)
            
            annotation = dt.datetime.now().strftime('%H:%M:%S %d.%m.%Y ') + " " + kName + " " + usage + ' ' + batVoltageString # calc annotation text (black bar)
            camera.annotate_text = annotation
            camera.wait_recording(1) #sleep a sec # 
  
        try:
            os.remove(oldOutputName+ '.h264') # remove the old tmp h264 file. (Had interval length time to convert it to mp4)
        except Exception as e: 
            log("WARNING: Konnte Datei nicht löschen: " + oldOutputName + " " + str(e))
            
        oldOutputName = outputName
        outputName = path + dt.datetime.now().strftime('%Y-%m-%d_%H-%M')
        
        camera.split_recording(outputName + '.h264')# record to new file
        
        if encrypt:
            try:
                cmdEncode = "MP4Box" + " -fps " + str(fps) +" -add " + oldOutputName + ".h264 " + oldOutputName + '.mp4'
                cmdEncrypt = "gpg" + " --output " + oldOutputName + '.mp4.gpg' + " --recipient " + receiver + " --encrypt " + oldOutputName + '.mp4'
                os.system(cmdEncode + ";" + cmdEncrypt)
                #subprocess.Popen(["MP4Box","-fps", str(fps),"-add",oldOutputName+ '.h264', oldOutputName+ '.mp4']) # convert h264 to mp4 format
                #log("INFO: " + oldOutputName + ".mp4 komplett." +  dt.datetime.now().strftime('%Y-%m-%d_%H-%M'))
                #subprocess.Popen(["gpg","--output", oldOutputName+ '.gpg',"--recipient", receiver, "--encrypt", oldOutputName+ '.mp4']) # convert h264 to mp4 format
                log("INFO: " + oldOutputName + ".gpg komplett." +  dt.datetime.now().strftime('%Y-%m-%d_%H-%M'))
            except Exception as e: 
                log("ERROR: Verschlüsselung fehlgeschlagen! " + oldOutputName + " " + str(e))
                oldOutputName = ""
        else:
            try:
                subprocess.Popen(["MP4Box","-fps", str(fps),"-add",oldOutputName+ '.h264', oldOutputName+ '.mp4']) # convert h264 to mp4 format
                log("INFO: " + oldOutputName + ".mp4 komplett." +  dt.datetime.now().strftime('%Y-%m-%d_%H-%M'))
            except Exception as e: 
                log("ERROR: Codierung fehlgeschlagen! " + oldOutputName + " " + str(e))
                oldOutputName = ""        


    camera.wait_recording(60) #at the end. record one more minute, just in case
    
    try:
        os.remove(oldOutputName+ '.h264') # remove tmp h264 file
        if encrypt:
            os.remove(oldOutputName+ '.mp4') # remove tmp mp4 file
    except Exception as e: 
        log("WARNING: Konnte Datei nicht löschen: " + oldOutputName + " " + str(e))
    
    
    log ("INFO: Stop recording now. " +  dt.datetime.now().strftime('%Y-%m-%d_%H-%M'))
    camera.stop_recording()
    
    #shutdown


