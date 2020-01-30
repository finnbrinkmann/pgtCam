import serial
from time import sleep
import datetime
import os
import time
from log import logAkku as logAkku
from time import sleep


def logBatLevel():

    #init data
    sp3_time = 0
    sp3_date = 0
    sp3_weekday = 0
    sp3_modus = 0
    sp3_alarm_enable = 0
    sp3_alarm_mode = 0
    sp3_alarm_hour = 0
    sp3_alarm_min = 0
    sp3_alarm_day = 0
    sp3_alarm_month = 0
    sp3_alarm_weekday = 0
    sp3_alarmPoweroff = 0
    sp3_alarm_hour_off = 0
    sp3_alarm_min_off = 0
    sp3_shutdown_enable = 0
    sp3_shutdown_time = 0
    sp3_warning_enable = 0
    sp3_serialLessMode = 0
    sp3_intervalAlarm = 0
    sp3_intervalAlarmOnTime = 0
    sp3_intervalAlarmOffTime = 0
    sp3_batLevel_shutdown = 0
    sp3_batLevel = 0
    sp3_charging = 0
    sp3_powerOnButton_enable = 0
    sp3_powerOnButton_time = 0
    sp3_poweroffMode = 0
    sp3_powersave_enable = 0
    sp3_ADC_Wide = 0
    sp3_ADC_BAT = 0
    sp3_ADC_USB = 0
    sp3_ADC_OUTPUT = 0
    sp3_output_status = 0
    sp3_powerfailure_counter = 0
    sp3_firmwareVersion = 0

    output_volt = "?"
    wide_range_volt_min = 4.8


    serial_port = serial.Serial()
    serial_port.baudrate = 38400
    serial_port.port = '/dev/serial0'
    serial_port.timeout = 1
    serial_port.bytesize = 8
    serial_port.stopbits = 1
    serial_port.parity = serial.PARITY_NONE

    if serial_port.isOpen(): serial_port.close()
    serial_port.open()

    #sometimes the strompi is to slow if you bombard him with data
    def writeSlow(content):

        content = list (content)
        
        for i in content:
            serial_port.write(str.encode(i))
            sleep(0.01)
        
        
        serial_port.write(str.encode('\x0D'))
        sleep(0.1)
    



    try:
        writeSlow('quit')
        #writeSlow('\x0D')
        writeSlow('status-rpi')
        #writeSlow('\x0D')
        

        timeout = 200 #timeout if no \n is received #default 9999

        #for firmware 1.72
        sp3_time = serial_port.readline(9999);
        sp3_date = serial_port.readline(9999);
        sp3_weekday = serial_port.readline(9999);
        sp3_modus = serial_port.readline(9999);
        sp3_alarm_enable = serial_port.readline(9999);
        sp3_alarm_mode = serial_port.readline(9999);
        sp3_alarm_hour = serial_port.readline(9999);
        sp3_alarm_min = serial_port.readline(9999);
        sp3_alarm_day = serial_port.readline(9999);
        sp3_alarm_month = serial_port.readline(9999);
        sp3_alarm_weekday = serial_port.readline(9999);
        sp3_alarmPoweroff = serial_port.readline(9999);
        sp3_alarm_hour_off = serial_port.readline(9999);
        sp3_alarm_min_off = serial_port.readline(9999);
        sp3_shutdown_enable = serial_port.readline(9999);
        sp3_shutdown_time = serial_port.readline(9999);
        sp3_warning_enable = serial_port.readline(9999);
        sp3_serialLessMode = serial_port.readline(9999);
        sp3_intervalAlarm = serial_port.readline(9999);
        sp3_intervalAlarmOnTime = serial_port.readline(9999);
        sp3_intervalAlarmOffTime = serial_port.readline(9999);
        sp3_batLevel_shutdown = serial_port.readline(9999);
        sp3_batLevel = serial_port.readline(9999);
        sp3_charging = serial_port.readline(9999);
        sp3_powerOnButton_enable = serial_port.readline(9999);
        sp3_powerOnButton_time = serial_port.readline(9999);
        sp3_powersave_enable = serial_port.readline(9999);
        sp3_poweroffMode = serial_port.readline(9999);
        sp3_poweroff_time_enable = serial_port.readline(9999);
        sp3_poweroff_time = serial_port.readline(9999);
        sp3_wakeupweekend_enable = serial_port.readline(9999);
        sp3_ADC_Wide = float(serial_port.readline(9999))/1000;
        sp3_ADC_BAT = float(serial_port.readline(9999))/1000;
        sp3_ADC_USB = float(serial_port.readline(9999))/1000;
        sp3_ADC_OUTPUT = float(serial_port.readline(9999))/1000;
        sp3_output_status = serial_port.readline(9999);
        sp3_powerfailure_counter = serial_port.readline(9999);
        sp3_firmwareVersion = serial_port.readline(9999);


    except:
        print("ERROR: Fehler beim Init der Abfrage der Batteriespannung")
    

    try:
        if sp3_ADC_Wide > wide_range_volt_min:
            wide_range_volt = str(sp3_ADC_Wide) 
        else:
            wide_range_volt = '0'

 
        logAkku(time.strftime("%Y-%m-%d %H:%M ") + wide_range_volt)


    except KeyboardInterrupt:
        print('interrupted!')
        
    except BaseException as e:
        print("ERROR: Fehler beim Abfragen der Batteriespannung" + str(e))

    serial_port.close()

    return (wide_range_volt)
        
