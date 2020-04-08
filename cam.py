#PYTHON3 !!!

import time
import picamera 
import datetime as dt
#import subprocess #system calls
import os
import subprocess
from log import log as log
import log2
from readVoltage import logBatLevel as logBat
import RPi.GPIO as GPIO

def recVideo(powerOffTime, fps, resX, resY, intervalLength, powersave, rot, msg, stromPi, kName, path, bw, receiver, encrypt, zero, bitrate):

    
    try:
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
            log2.logger.error("Cameraparameter fehlerhaft. " + str(e))
        
        
        log2.logger.info("Aufzeichnung wird vorbereitet.")
        batVoltageString = ""
        #log (str(stromPi))
        
        if stromPi:
            camera.annotate_text = "Abfrage der Batteriespannung..."
            batVoltage = logBat()
            batVoltageString = str(batVoltage)[:4] + "V"
        
        camera.annotate_text = "Aufzeichnung wird vorbereitet..."
        
        outputName = ""
        oldOutputName = ""

        try:
            diskFree = int(os.popen("df --output=avail /dev/sda1 |tail -n 1").read().strip()) #get harddisk free space. 
            diskUsed = int(os.popen("df --output=used /dev/sda1 |tail -n 1").read().strip()) #get harddisk used space
            usage = str(int(diskFree / (diskFree + diskUsed) *100 )) + "%"
            
        except Exception as e:

            log2.logger.error("Fehler beim Abfragen vom USB-Speicherplatz. " + str(e))
            usage = 'USB-FEHLER'


        #wait for next 15 min interval
        tm = dt.datetime.now()


        tm = tm - dt.timedelta(minutes=(tm.minute % 15)-30, seconds=tm.second, microseconds=tm.microsecond) # calc time of next 0/15/30/45min (and add additional 15min)
        #tm = tm - dt.timedelta(minutes=(tm.minute % 15)-15, seconds=tm.second, microseconds=tm.microsecond) #for debug, to speed up dev time

        try:
            path = path + kName + '/'
            os.makedirs(path, exist_ok=True) # create folder if does not exist
            outputName = path + kName + '_' + dt.datetime.now().strftime('%Y-%m-%d_%H-%M')
        except Exception as e:
            log2.logger.error("Konnte Ordner nicht anlegen. USB-Stick fehlerhaft? " + str(e))
        
        try:
            
            camera.start_recording(outputName  + '.h264', bitrate=bitrate)
        except Exception as e:
            log2.logger.error("Aufnahmefehler. USB-Stick noch vorhanden?! " + str(e))
            
            
        #loop until next 00/15/30/45min is reached
        while True:
            time.sleep(1)
            fileSize = os.path.getsize(outputName + '.h264') % 100 #to limit output to 2 numbers
            #log("filesize = " + str(fileSize))
            annotation = dt.datetime.now().strftime('%H:%M:%S %d.%m.%Y ') + " " + kName + ' ' + usage + ' ' + batVoltageString + ' ' +str(fileSize) + ' ' + msg
            camera.annotate_text = annotation
            if tm < dt.datetime.now(): 
                break

        end = time.time() # seconds since 1970

        log2.logger.info("Starte die Aufnahme")
        oldOutputName = outputName #remember old file in order to encode and delete
        outputName = path + kName + '_' + dt.datetime.now().strftime('%Y-%m-%d_%H-%M')
        camera.split_recording(outputName  + '.h264') # create a new file every intervalLength (15) min
        
        #try:
        #    subprocess.Popen(["MP4Box","-fps", str(fps),"-add",oldOutputName + '.h264', oldOutputName + '.mp4']) # convert h264 to mp4 format. 
        #    log2.logger.info("" + oldOutputName + ".mp4 komplett." +  dt.datetime.now().strftime('%Y-%m-%d_%H-%M'))
        #except Exception as e: 
        #    log2.logger.error("Codierung fehlgeschlagen! " + oldOutputName + " " + str(e))
        #    oldOutputName = "" # prevent deletion of file
            
            
        if encrypt:
            try:
                cmdEncode = "MP4Box" + " -fps " + str(25) +" -add " + oldOutputName + ".h264 " + oldOutputName + '.mp4'
                cmdEncrypt = "gpg" + " --output " + oldOutputName + '.mp4.gpg' + " --recipient " + receiver + " --encrypt " + oldOutputName + '.mp4'
                os.system(cmdEncode + ";" + cmdEncrypt)
                #subprocess.Popen(["MP4Box","-fps", str(fps),"-add",oldOutputName+ '.h264', oldOutputName+ '.mp4']) # convert h264 to mp4 format
                #log2.logger.info("" + oldOutputName + ".mp4 komplett." +  dt.datetime.now().strftime('%Y-%m-%d_%H-%M'))
                #subprocess.Popen(["gpg","--output", oldOutputName+ '.gpg',"--recipient", receiver, "--encrypt", oldOutputName+ '.mp4']) # convert h264 to mp4 format
                log2.logger.info("" + oldOutputName + ".gpg komplett." +  dt.datetime.now().strftime('%Y-%m-%d_%H-%M'))
            except Exception as e: 
                log2.logger.error("Verschlüsselung fehlgeschlagen! " + oldOutputName + " " + str(e))
                oldOutputName = "" # change name in case of an error to prevent the from deletetion
        else:
            try:
                subprocess.Popen(["MP4Box","-fps", str(25),"-add",oldOutputName+ '.h264', oldOutputName+ '.mp4']) # convert h264 to mp4 format
                log2.logger.info("" + oldOutputName + ".mp4 komplett." +  dt.datetime.now().strftime('%Y-%m-%d_%H-%M'))
            except Exception as e: 
                log2.logger.error("Codierung fehlgeschlagen! " + oldOutputName + " " + str(e))
                oldOutputName = ""        


        if powersave: # activate powersave mode if set in conig txt. 
            try:
                
                if zero:
                
                    #os.system('echo 0 | sudo tee /sys/class/leds/led0/brightness') #activate green RPi onboard LED RPIzero first
                    os.system('echo none | sudo tee /sys/class/leds/led0/trigger') #deactivate green RPi onboard LED RPIzero
                    os.system('echo 1 | sudo tee /sys/class/leds/led0/brightness') #deactivate green RPi onboard LED RPIzero
                    
                    GPIO.setmode(GPIO.BCM) #deactivate camera led
                    GPIO.setup(40, GPIO.OUT, initial=False)
                    
                else:
                

                    os.system('echo none | sudo tee /sys/class/leds/led0/trigger') #deaktivate trigger
                    os.system('echo none | sudo tee /sys/class/leds/led1/trigger') #deaktivate trigger
                    os.system('echo 0 | sudo tee /sys/class/leds/led0/brightness') #deactivate green RPi onboard LED on RPi2
                    os.system('echo 0 | sudo tee /sys/class/leds/led1/brightness') #deactivate green RPi onboard LED

                    camera.led = False #deactivate camera led
                    
                os.system('/usr/bin/tvservice -o') # deactivate display ports
                
                log2.logger.info("POWERSAVE aktiviert")
            except Exception as e:
                log2.logger.warning("PowerSave Fehler. " + str(e))

        #camera.wait_recording(1)
        log2.logger.info("Aufzeichnen läuft bis: " + str(powerOffTime))

    ############### Record loop
        while dt.datetime.now() < powerOffTime: # until time off date is reached

            if stromPi:
                batVoltage = logBat() # log the Battery voltage #braucht das sehr lange wenn kein strom pi angeschlossen ist?!
                batVoltageString = str(batVoltage)[:4] + "V" #4 letters e.g. 13.9V 
                
            end = end + intervalLength * 60 # add 15 min * 60 sec/min
            
            
            try:
                diskFree = int(os.popen("df --output=avail /dev/sda1 |tail -n 1").read().strip()) #get harddisk free space. 
                diskUsed = int(os.popen("df --output=used /dev/sda1 |tail -n 1").read().strip()) #get harddisk used space
                usage = str(int(diskFree / (diskFree + diskUsed) *100 )) + "%"
                
            except Exception as e:
                log2.logger.warning("Fehler in Speicherplatzabfrage. " + str(e))
                usage = "?%"
                #raise
                #a reboot might be necessary

            log2.logger.debug("Loop now")
            
            while time.time() < end : # while 15min (or intervall length)
                
                annotation = dt.datetime.now().strftime('%H:%M:%S %d.%m.%Y ') + " " + kName + " " + usage + ' ' + batVoltageString # calc annotation text (black bar)
                camera.annotate_text = annotation
                camera.wait_recording(1) #sleep a sec # 

            log2.logger.debug("Interval complete")
            
            try:
                os.remove(oldOutputName+ '.h264') # remove the old tmp h264 file. (Had interval length time to convert it to mp4)
                if encrypt:
                    os.remove(oldOutputName+ '.mp4') # remove tmp mp4 file
            except Exception as e: 
                log2.logger.warning("Konnte Datei nicht löschen: " + oldOutputName + " " + str(e))
            
            log2.logger.debug("genOutput names")

            oldOutputName = outputName
            outputName = path + kName + '_' + dt.datetime.now().strftime('%Y-%m-%d_%H-%M')
            log2.logger.debug("Split Rec")
            camera.split_recording(outputName + '.h264')# record to new file
            
            if encrypt:
                try:
                    #cmdEncode = "MP4Box" + " -fps " + str(fps) +" -add " + oldOutputName + ".h264 " + oldOutputName + '.mp4' # encode with correct fps
                    cmdEncode = "MP4Box" + " -fps " + str(25) +" -add " + oldOutputName + ".h264 " + oldOutputName + '.mp4' # encode with fake old vlc/h264 playbackspeed
                    cmdEncrypt = "gpg" + " --output " + oldOutputName + '.mp4.gpg' + " --recipient " + receiver + " --encrypt " + oldOutputName + '.mp4'
                    os.system(cmdEncode + ";" + cmdEncrypt)
                    #subprocess.Popen(["MP4Box","-fps", str(fps),"-add",oldOutputName+ '.h264', oldOutputName+ '.mp4']) # convert h264 to mp4 format
                    #log2.logger.info("" + oldOutputName + ".mp4 komplett." +  dt.datetime.now().strftime('%Y-%m-%d_%H-%M'))
                    #subprocess.Popen(["gpg","--output", oldOutputName+ '.gpg',"--recipient", receiver, "--encrypt", oldOutputName+ '.mp4']) # convert h264 to mp4 format
                    log2.logger.info("" + oldOutputName + ".gpg komplett.")
                except Exception as e: 
                    log2.logger.error("Verschlüsselung fehlgeschlagen! " + oldOutputName + " " + str(e))
                    oldOutputName = ""
            else:
                try:
                    #subprocess.Popen(["MP4Box","-fps", str(fps),"-add",oldOutputName+ '.h264', oldOutputName+ '.mp4']) # convert h264 to mp4 format
                    subprocess.Popen(["MP4Box","-fps", str(25),"-add",oldOutputName+ '.h264', oldOutputName+ '.mp4']) # convert h264 to mp4 format # encode with fake old vlc/h264 playbackspeed
                    log2.logger.info("" + oldOutputName + ".mp4 komplett.")
                except Exception as e: 
                    log2.logger.error("Codierung fehlgeschlagen! " + oldOutputName + " " + str(e))
                    oldOutputName = ""        


        camera.wait_recording(60) #at the end. record one more minute, just in case
        
        try:
            os.remove(oldOutputName+ '.h264') # remove tmp h264 file
            if encrypt:
                os.remove(oldOutputName+ '.mp4') # remove tmp mp4 file
        except Exception as e: 
            log2.logger.warning("Konnte Datei nicht löschen: " + oldOutputName + " " + str(e))
        
        
        log2.logger.info("Stop recording now.")
        
        camera.stop_recording()

        time.sleep(30)
        camera.close() 
        
    except Exception as e: 
        log2.logger.error("Fehler in Cam: " + str(e))
        try:
            camera.stop_recording()
        except Exception as e: 
            log2.logger.warning("no recording to stop: " + str(e))
        try:    
            camera.stop_preview()
        except Exception as e: 
            log2.logger.warning("no preview to stop: " + str(e))
            
        time.sleep(10)
        
        try:
            camera.close() 
            log2.logger.info("camera geschlossen: ")
        except Exception as e: 
            log2.logger.error("Camera konnte nicht geschlossen werden!: " + str(e))
            
        raise




