import serial
import threading
from time import sleep
import time
import datetime
import os
from log import log as log

def syncClock():

    
    try:
        log("INFO: Syncronisiere Uhren")

        serial_port = serial.Serial()

        serial_port.baudrate = 38400
        #serial_port.port = '/dev/serial0'
        serial_port.port = '/dev/ttyAMA0'
        serial_port.timeout = 1
        serial_port.bytesize = 8
        serial_port.stopbits = 1
        serial_port.parity = serial.PARITY_NONE

        if serial_port.isOpen(): serial_port.close()
        serial_port.open()
    except Exception as e:
    
        log("ERROR: syncClock error. "  + str(e))

    def writeSlow(content):

        content = list (content)
        
        for i in content:
            serial_port.write(str.encode(i))
            sleep(0.01)
        
        
        serial_port.write(str.encode('\x0D'))
        sleep(0.5)



    try:


        i = 0 
        while i < 5:   # try 5 times to get the data
            try:
                writeSlow('date-rpi')
                data = serial_port.read(9999);
                date = int(data)
                strompi_year = date // 10000
                strompi_month = date % 10000 // 100
                strompi_day = date % 100
            
                log("INFO: StromPi Datum: " + str(strompi_day) + "." + str(strompi_month) + "." + str(strompi_year))
                break            
                
            except Exception as e:
                log ("ERROR: Fehler beim Syncronisieren des Datums. Versuch: " + str(i) + " " + str(data) + " " + str(e))
                i = i + 1
                continue


        i = 0 
        while i < 5:    # try 5 times to get the data
            try:
                writeSlow('time-rpi')
                data = serial_port.read(9999);

                timevalue = int(data)

                strompi_hour = timevalue // 10000
                strompi_min = timevalue % 10000 // 100
                strompi_sec = timevalue % 100
                
                log("INFO: StromPi Zeit: " + str(strompi_hour) + ":" + str(strompi_min) + ":" + str(strompi_sec))
                break

            except Exception as e:
                
                log ("ERROR: Fehler beim Syncronisieren der Zeit. Versuch: " + str(i) + " " + str(data)+ " " + str(e))
                i = i + 1
                continue


        rpi_time = datetime.datetime.now().replace(microsecond=0)
        strompi_time = datetime.datetime(2000 + strompi_year, strompi_month, strompi_day, strompi_hour, strompi_min, strompi_sec, 0)
        
        command = 'set-time %02d %02d %02d' % (int(rpi_time.strftime('%H')),int(rpi_time.strftime('%M')),int(rpi_time.strftime('%S')))

        if rpi_time > strompi_time:
            writeSlow('set-date %02d %02d %02d %02d' % (int(rpi_time.strftime('%d')),int(rpi_time.strftime('%m')),int(rpi_time.strftime('%Y'))%100,int(rpi_time.isoweekday())))
            writeSlow('set-clock %02d %02d %02d' % (int(rpi_time.strftime('%H')),int(rpi_time.strftime('%M')),int(rpi_time.strftime('%S'))))
            
            log ('INFO: The date und time has been synced: Raspberry Pi -> StromPi')
            
        else:
            os.system('sudo date +%%y%%m%%d --set=%02d%02d%02d' % (strompi_year, strompi_month, strompi_day))
            os.system('sudo date +%%T -s "%02d:%02d:%02d"' % (strompi_hour, strompi_min, strompi_sec))
            
            log ('WARNING: The date und time has been synced: StromPi -> Raspberry Pi')
            

    except KeyboardInterrupt:
        log('interrupted!')
    except ValueError:
        log('ERROR: in sync time! ValueError')
        pass
    except OverflowError:
        log('ERROR: in sync time! OverflowError')
        log (data)
        pass
    except Exception as e:
        log ('ERROR: Unexpected error in Sycn Time.' + str(e))
        pass
        
    serial_port.close()