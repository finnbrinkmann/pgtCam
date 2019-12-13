#!/usr/bin/python3

import os

from strompi_config import writeSP
from stromStatus2 import getData
from time import sleep



while True: #loopbreak until a stick is found    
    if os.path.ismount("/media/stick/"):
        try:
            f = open('/media/stick/akkuLog.txt', 'w')
            print ("INFO: /media/stick/akkuLog.txt geöffnet")
            
        except IOError:
            print ("ERROR: Kann Datei nicht lesen /media/stick/config.txt. Datei vorhanden?")
            
        break
    else:
        
        sleep(5)
        print("INFO: Keinen USB-Stick gefunden")
        #exit()

while True:
    getData()
    

    # try:
        # s = str(s)
        # print(s)
    # except:
        # print("Error: Can not cast log data to string")
                
    # try:

        # f.write(s + '\n')

    # except:
        # print ("ERROR: Could not write data to akkuLog")


    sleep(60)
        
        
f.close()