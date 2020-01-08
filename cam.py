#PYTHON3 !!!

import time
import picamera 
import datetime as dt
#import subprocess #system calls
import os
import subprocess
from log import log as log
from readVoltage import logBatLevel as logBat


def recVideo(powerOffTime, fps, resX, resY, intervalLength, powersave, rot, msg, stromPi, kName):

    
    
    #camera is activated
    camera = picamera.PiCamera()
    camera.rotation = rot
    camera.resolution = (resX, resY) #4x3 size 
    camera.framerate = fps
    
    camera.start_preview(alpha = 250) #transparent preview
    camera.annotate_background = picamera.Color('black')
    
    
    log ("INFO: Aufzeichnung wird vorbereitet.")
    batVoltage = logBat()
    

    try:
        diskFree = int(os.popen("df --output=avail /dev/sda1 |tail -n 1").read().strip()) #get harddisk free space. 
        diskUsed = int(os.popen("df --output=used /dev/sda1 |tail -n 1").read().strip()) #get harddisk used space
        usage = str(int(diskFree / (diskFree + diskUsed) *100 )) + "%"
        
    except Exception as e:

        log ("Error: Fehler beim Abfragen vom USB-Speicherplatz " + str(e))
        usage = 'USB-FEHLER'


    #wait for next 15 min interval
    tm = dt.datetime.now()


    tm = tm - dt.timedelta(minutes=(tm.minute % 15)-15,
                                 seconds=tm.second,
                                 microseconds=tm.microsecond)



    
    try:
        path = '/media/stick/' + kName + '/'
        os.makedirs(path, exist_ok=True) # create folder if does not exist
        outputName = path + dt.datetime.now().strftime('%Y-%m-%d_%H-%M') + 'preview'
    except Exception as e:
        log("ERROR: Konnte Ordner nicht anlegen. USB-Stick fehlerhaft? " + str(e))
    
    try:
        camera.start_recording(outputName  + '.h264')
    except Exception as e:
        print ("ERROR: Aufnahmefehler. USB-Stick?! Reboot? " + str(e))
        #os.system('sudo reboot')
        
    #loop until next 00/15/30/45min is reached
    while True:
        time.sleep(1)
        fileSize = os.path.getsize(outputName + '.h264') % 100 #to limit output to 2 numbers
        #log("filesize = " + str(fileSize))
        annotation = dt.datetime.now().strftime('%H:%M:%S %d.%m.%Y ') + " " + kName + ' ' + usage + ' ' + batVoltage + 'V ' + str(fileSize) + ' ' + msg
        camera.annotate_text = annotation
        if tm < dt.datetime.now(): 
            break




    end = time.time() # seconds since 1970

    log ("INFO: Start recording now")
    oldOutputName = outputName
    outputName = path + dt.datetime.now().strftime('%Y-%m-%d_%H-%M')
    camera.split_recording(outputName  + '.h264') 
    
    try:
        subprocess.Popen(["MP4Box","-fps", str(fps),"-add",oldOutputName + '.h264', oldOutputName + '.mp4']) # convert h264 to mp4 format
        log("INFO: " + oldOutputName + ".mp4 komplett." +  dt.datetime.now().strftime('%Y-%m-%d_%H-%M'))
    except Exception as e: 
        log("ERROR: Codierung fehlgeschlagen! " + oldOutputName + " " + str(e))
        oldOutputName = ""


    log("INFO: " + oldOutputName + ".mp4 komplett." +  dt.datetime.now().strftime('%Y-%m-%d_%H-%M'))

    if powersave: # activate powersave mode if set in conig txt. 
        try:
            os.system('echo 1 | sudo tee /sys/class/leds/led0/brightness') #deactivate green RPi onboard LED
            os.system('/usr/bin/tvservice -o') # deactivate display ports
            log("INFO: POWERSAVE on")
        except Exception as e:
            log("WARNING: PowerSave Error. " + str(e))

    #camera.wait_recording(1)
    log("INFO: Aufzeichnen läuft bis: " + str(powerOffTime))

    while dt.datetime.now() < powerOffTime: # until time off date is reached

        batVoltage = logBat() # log the Battery voltage #braucht das sehr lange wenn kein strom pi angeschlossen ist?!
        end = end + intervalLength * 60 # add 15 min * 60 sec/min
        
        
        try:
            diskFree = int(os.popen("df --output=avail /dev/sda1 |tail -n 1").read().strip()) #get harddisk free space. 
            diskUsed = int(os.popen("df --output=used /dev/sda1 |tail -n 1").read().strip()) #get harddisk used space
            usage = str(int(diskFree / (diskFree + diskUsed) *100 )) + "%"
            
        except Exception as e:
            log("WARNING: Fehler in Speicherplatzabfrage" + str(e))
            usage = "?%"
            
        while time.time() < end : # while 15min (or intervall length)
            
            annotation = dt.datetime.now().strftime('%H:%M:%S %d.%m.%Y ') + " " + kName + " " + usage + ' ' + batVoltage + 'V' # calc annotation text (black bar)
            camera.annotate_text = annotation
            camera.wait_recording(1) #sleep a sec # 
  
        try:
            os.remove(oldOutputName+ '.h264') # remove the old tmp h264 file. (Had interval length time to convert it to mp4)
        except Exception as e: 
            log("WARNING: Konnte Datei nicht löschen: " + oldOutputName + " " + str(e))
            
        oldOutputName = outputName
        outputName = path + dt.datetime.now().strftime('%Y-%m-%d_%H-%M')
        
        camera.split_recording(outputName + '.h264')# record to new file
        try:
            subprocess.Popen(["MP4Box","-fps", str(fps),"-add",oldOutputName+ '.h264', oldOutputName+ '.mp4']) # convert h264 to mp4 format
            log("INFO: " + oldOutputName + ".mp4 komplett." +  dt.datetime.now().strftime('%Y-%m-%d_%H-%M'))
        except Exception as e: 
            log("ERROR: Codierung fehlgeschlagen! " + oldOutputName + " " + str(e))
            oldOutputName = ""


    camera.wait_recording(60) #at the end. record one more minute, just in case
    
    try:
        os.remove(oldOutputName+ '.h264') # remove tmp h264 file
    except Exception as e: 
        log("WARNING: Konnte Datei nicht löschen: " + oldOutputName + " " + str(e))
    
    
    log ("INFO: Stop recording now. " +  dt.datetime.now().strftime('%Y-%m-%d_%H-%M'))
    camera.stop_recording()
    
    #shutdown


