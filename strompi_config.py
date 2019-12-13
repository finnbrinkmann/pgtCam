import serial
from time import sleep
import datetime
import os
import time
from time import sleep

def writeSP(month, day, hour, minute):

    wide_range_volt_min = 4.8
    battery_volt_min = 0.5
    mUSB_volt_min = 4.1

    breakS = 0.1
    breakL = 0.5

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



    #######################################################################################################################
    serial_port.write(str.encode('quit'))
    sleep(breakS)
    serial_port.write(str.encode('\x0D'))
    sleep(breakL)


    try:

    #######################################################################################################################

        print('\n----------------------------------------------')
        print(' Transfer new Configuration to the StromPi 3')
        print(' \n###Please Wait###')
        print('-----------------------------------------------')

        breakS = 0.1
        breakL = 0.2

        sp3_modus = '1'
        sp3_alarm_mode = 2
        sp3_alarmPoweroff = '0'
        sp3_alarm_min  = minute
        sp3_alarm_hour  = hour
        sp3_alarm_min_off  = '0'
        sp3_alarm_hour_off  = '0'
        sp3_alarm_day  = day
        sp3_alarm_month  = month
        sp3_alarm_weekday  = '0'
        sp3_alarm_enable  = '1'
        sp3_shutdown_enable  = '0'
        sp3_shutdown_time  = '5'
        sp3_warning_enable  = '0'
        sp3_serialLessMode  = '0'
        sp3_batLevel_shutdown  = '0'
        sp3_intervalAlarm  = '0'
        sp3_intervalAlarmOnTime  = '0'
        sp3_intervalAlarmOffTime  = '0'
        sp3_powerOnButton_enable  = '0'
        sp3_powerOnButton_time  = '0'
        sp3_powersave_enable  = '0'
        sp3_poweroffMode  = '0'
        modusreset = 0

        if type(sp3_modus) == str:
            serial_port.write(str.encode('set-config ' + '1 ' +  sp3_modus))
        else:
            serial_port.write(str.encode('set-config ' + '1 ' + sp3_modus.decode(encoding='UTF-8', errors='strict')))
        sleep(breakS)
        serial_port.write(str.encode('\x0D'))
        sleep(breakL)


        if sp3_alarm_mode == 1:
            serial_port.write(str.encode('set-config ' + '2 0'))
            sleep(breakS)
            serial_port.write(str.encode('\x0D'))
            sleep(breakL)

            serial_port.write(str.encode('set-config ' + '3 0'))
            sleep(breakS)
            serial_port.write(str.encode('\x0D'))
            sleep(breakL)

            serial_port.write(str.encode('set-config ' + '4 1'))
            sleep(breakS)
            serial_port.write(str.encode('\x0D'))
            sleep(breakL)

        elif sp3_alarm_mode == 2:
            serial_port.write(str.encode('set-config ' + '2 1'))
            sleep(breakS)
            serial_port.write(str.encode('\x0D'))
            sleep(breakL)

            serial_port.write(str.encode('set-config ' + '3 0'))
            sleep(breakS)
            serial_port.write(str.encode('\x0D'))
            sleep(breakL)

            serial_port.write(str.encode('set-config ' + '4 0'))
            sleep(breakS)
            serial_port.write(str.encode('\x0D'))
            sleep(breakL)

        elif sp3_alarm_mode == 3:
            serial_port.write(str.encode('set-config ' + '2 0'))
            sleep(breakS)
            serial_port.write(str.encode('\x0D'))
            sleep(breakL)

            serial_port.write(str.encode('set-config ' + '3 1'))
            sleep(breakS)
            serial_port.write(str.encode('\x0D'))
            sleep(breakL)

            serial_port.write(str.encode('set-config ' + '4 0'))
            sleep(breakS)
            serial_port.write(str.encode('\x0D'))
            sleep(breakL)

        if type(sp3_alarmPoweroff) == str:
            serial_port.write(str.encode('set-config ' + '5 ' +  sp3_alarmPoweroff))
        else:
            serial_port.write(str.encode('set-config ' + '5 ' + sp3_alarmPoweroff.decode(encoding='UTF-8', errors='strict')))
        sleep(breakS)
        serial_port.write(str.encode('\x0D'))
        sleep(breakL)

        if type(sp3_alarm_min) == str:
            serial_port.write(str.encode('set-config ' + '6 ' +  sp3_alarm_min))
        else:
            serial_port.write(str.encode('set-config ' + '6 ' + sp3_alarm_min.decode(encoding='UTF-8', errors='strict')))
        sleep(breakS)
        serial_port.write(str.encode('\x0D'))
        sleep(breakL)

        if type(sp3_alarm_hour) == str:
            serial_port.write(str.encode('set-config ' + '7 ' +  sp3_alarm_hour))
        else:
            serial_port.write(str.encode('set-config ' + '7 ' + sp3_alarm_hour.decode(encoding='UTF-8', errors='strict')))
        sleep(breakS)
        serial_port.write(str.encode('\x0D'))
        sleep(breakL)

        if type(sp3_alarm_min_off) == str:
            serial_port.write(str.encode('set-config ' + '8 ' + sp3_alarm_min_off))
        else:
            serial_port.write(str.encode('set-config ' + '8 ' + sp3_alarm_min_off.decode(encoding='UTF-8', errors='strict')))
        sleep(breakS)
        serial_port.write(str.encode('\x0D'))
        sleep(breakL)

        if type(sp3_alarm_hour_off) == str:
            serial_port.write(str.encode('set-config ' + '9 ' + sp3_alarm_hour_off))
        else:
            serial_port.write(str.encode('set-config ' + '9 ' + sp3_alarm_hour_off.decode(encoding='UTF-8', errors='strict')))
        sleep(breakS)
        serial_port.write(str.encode('\x0D'))
        sleep(breakL)

        if type(sp3_alarm_day) == str:
            serial_port.write(str.encode('set-config ' + '10 ' + sp3_alarm_day))
        else:
            serial_port.write(str.encode('set-config ' + '10 ' + sp3_alarm_day.decode(encoding='UTF-8', errors='strict')))
        sleep(breakS)
        serial_port.write(str.encode('\x0D'))
        sleep(breakL)

        if type(sp3_alarm_month) == str:
            serial_port.write(str.encode('set-config ' + '11 ' + sp3_alarm_month))
        else:
            serial_port.write(str.encode('set-config ' + '11 ' + sp3_alarm_month.decode(encoding='UTF-8', errors='strict')))
        sleep(breakS)
        serial_port.write(str.encode('\x0D'))
        sleep(breakL)

        if type(sp3_alarm_weekday) == str:
            serial_port.write(str.encode('set-config ' + '12 ' + sp3_alarm_weekday))
        else:
            serial_port.write(str.encode('set-config ' + '12 ' + sp3_alarm_weekday.decode(encoding='UTF-8', errors='strict')))
        sleep(breakS)
        serial_port.write(str.encode('\x0D'))
        sleep(breakL)

        if type(sp3_alarm_enable) == str:
            serial_port.write(str.encode('set-config ' + '13 ' + sp3_alarm_enable))
        else:
            serial_port.write(str.encode('set-config ' + '13 ' + sp3_alarm_enable.decode(encoding='UTF-8', errors='strict')))
        sleep(breakS)
        serial_port.write(str.encode('\x0D'))
        sleep(breakL)

        if type(sp3_shutdown_enable) == str:
            serial_port.write(str.encode('set-config ' + '14 ' + sp3_shutdown_enable))
        else:
            serial_port.write(str.encode('set-config ' + '14 ' + sp3_shutdown_enable.decode(encoding='UTF-8', errors='strict')))
        sleep(breakS)
        serial_port.write(str.encode('\x0D'))
        sleep(breakL)

        if type(sp3_shutdown_time) == str:
            serial_port.write(str.encode('set-config ' + '15 ' + sp3_shutdown_time))
        else:
            serial_port.write(str.encode('set-config ' + '15 ' + sp3_shutdown_time.decode(encoding='UTF-8', errors='strict')))
        sleep(breakS)
        serial_port.write(str.encode('\x0D'))
        sleep(breakL)

        if type(sp3_warning_enable) == str:
            serial_port.write(str.encode('set-config ' + '16 ' + sp3_warning_enable))
        else:
            serial_port.write(str.encode('set-config ' + '16 ' + sp3_warning_enable.decode(encoding='UTF-8', errors='strict')))
        sleep(breakS)
        serial_port.write(str.encode('\x0D'))
        sleep(breakL)

        if type(sp3_serialLessMode) == str:
            serial_port.write(str.encode('set-config ' + '17 ' + sp3_serialLessMode))
        else:
            serial_port.write(str.encode('set-config ' + '17 ' + sp3_serialLessMode.decode(encoding='UTF-8', errors='strict')))
        sleep(breakS)
        serial_port.write(str.encode('\x0D'))
        sleep(breakL)

        if type(sp3_batLevel_shutdown) == str:
            serial_port.write(str.encode('set-config ' + '18 ' + sp3_batLevel_shutdown))
        else:
            serial_port.write(str.encode('set-config ' + '18 ' + sp3_batLevel_shutdown.decode(encoding='UTF-8', errors='strict')))
        sleep(breakS)
        serial_port.write(str.encode('\x0D'))
        sleep(breakL)

        if type(sp3_intervalAlarm) == str:
            serial_port.write(str.encode('set-config ' + '19 ' + sp3_intervalAlarm))
        else:
            serial_port.write(str.encode('set-config ' + '19 ' + sp3_intervalAlarm.decode(encoding='UTF-8', errors='strict')))
        sleep(breakS)
        serial_port.write(str.encode('\x0D'))
        sleep(breakL)

        if type(sp3_intervalAlarmOnTime) == str:
            serial_port.write(str.encode('set-config ' + '20 ' + sp3_intervalAlarmOnTime))
        else:
            serial_port.write(str.encode('set-config ' + '20 ' + sp3_intervalAlarmOnTime.decode(encoding='UTF-8', errors='strict')))
        sleep(breakS)
        serial_port.write(str.encode('\x0D'))
        sleep(breakL)

        if type(sp3_intervalAlarmOffTime) == str:
            serial_port.write(str.encode('set-config ' + '21 ' + sp3_intervalAlarmOffTime))
        else:
            serial_port.write(str.encode('set-config ' + '21 ' + sp3_intervalAlarmOffTime.decode(encoding='UTF-8', errors='strict')))
        sleep(breakS)
        serial_port.write(str.encode('\x0D'))
        sleep(breakL)

        if type(sp3_powerOnButton_enable) == str:
            serial_port.write(str.encode('set-config ' + '22 ' + sp3_powerOnButton_enable))
        else:
            serial_port.write(str.encode('set-config ' + '22 ' + sp3_powerOnButton_enable.decode(encoding='UTF-8', errors='strict')))
        sleep(breakS)
        serial_port.write(str.encode('\x0D'))
        sleep(breakL)

        if type(sp3_powerOnButton_time) == str:
            serial_port.write(str.encode('set-config ' + '23 ' + sp3_powerOnButton_time))
        else:
            serial_port.write(str.encode('set-config ' + '23 ' + sp3_powerOnButton_time.decode(encoding='UTF-8', errors='strict')))
        sleep(breakS)
        serial_port.write(str.encode('\x0D'))
        sleep(breakL)

        if type(sp3_powersave_enable) == str:
            serial_port.write(str.encode('set-config ' + '24 ' + sp3_powersave_enable))
        else:
            serial_port.write(str.encode('set-config ' + '24 ' + sp3_powersave_enable.decode(encoding='UTF-8', errors='strict')))
        sleep(breakS)
        serial_port.write(str.encode('\x0D'))
        sleep(breakL)
        
        if type(sp3_poweroffMode) == str:
            serial_port.write(str.encode('set-config ' + '25 ' + sp3_poweroffMode))
        else:
            serial_port.write(str.encode('set-config ' + '25 ' + sp3_poweroffMode.decode(encoding='UTF-8', errors='strict')))
        sleep(breakS)
        serial_port.write(str.encode('\x0D'))
        sleep(breakL)
        
        
        if modusreset == 1:
            serial_port.write(str.encode('set-config ' + '0 1'))
            sleep(breakS)
            serial_port.write(str.encode('\x0D'))
            sleep(breakL)


        elif modusreset != 1:
            serial_port.write(str.encode('set-config ' + '0 0'))
            sleep(breakS)
            serial_port.write(str.encode('\x0D'))
            sleep(breakL)

        print(' Configuration Successful')

    except KeyboardInterrupt:
        print('interrupted!')

    serial_port.close()