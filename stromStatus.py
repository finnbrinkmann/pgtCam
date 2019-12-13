import serial
from time import sleep
import datetime
import os
import time
from time import sleep
from log import log as log


class stromPi:

    def __init__(self):
        #init data
        self.sp3_time = 0
        self.sp3_date = 0
        self.sp3_weekday = 0
        self.sp3_modus = 0
        self.sp3_alarm_enable = 0
        self.sp3_alarm_mode = 0
        self.sp3_alarm_hour = 0
        self.sp3_alarm_min = 0
        self.sp3_alarm_day = 0
        self.sp3_alarm_month = 0
        self.sp3_alarm_weekday = 0
        self.sp3_alarmPoweroff = 0
        self.sp3_alarm_hour_off = 0
        self.sp3_alarm_min_off = 0
        self.sp3_shutdown_enable = 0
        self.sp3_shutdown_time = 0
        self.sp3_warning_enable = 0
        self.sp3_serialLessMode = 0
        self.sp3_intervalAlarm = 0
        self.sp3_intervalAlarmOnTime = 0
        self.sp3_intervalAlarmOffTime = 0
        self.sp3_batLevel_shutdown = 0
        self.sp3_batLevel = 0
        self.sp3_charging = 0
        self.sp3_powerOnButton_enable = 0
        self.sp3_powerOnButton_time = 0
        self.sp3_poweroffMode = 0
        self.sp3_powersave_enable = 0
        self.sp3_ADC_Wide = 0
        self.sp3_ADC_BAT = 0
        self.sp3_ADC_USB = 0
        self.sp3_ADC_OUTPUT = 0
        self.sp3_output_status = 0
        self.sp3_powerfailure_counter = 0
        self.sp3_firmwareVersion = 0
        
        self.output_volt = "?"

        try:
            log("Öffne serielle Schnittstelle")
            self.serial_port = serial.Serial()

            self.serial_port.baudrate = 38400
            #serial_port.port = '/dev/serial0'
            serial_port.port = '/dev/ttyAMA0'
            self.serial_port.timeout = 1
            self.serial_port.bytesize = 8
            self.serial_port.stopbits = 1
            self.serial_port.parity = serial.PARITY_NONE

            if self.serial_port.isOpen(): self.serial_port.close()
            self.serial_port.open()
            self.open = True
        except Exception as e:

            log ("Error: Fehler in der seriellen Kommunikation. " + str(e))
            self.open = False


    def writeSlow(content):

        content = list (content)
        
        for i in content:
            serial_port.write(str.encode(i))
            sleep(0.01)
        
        
        serial_port.write(str.encode('\x0D'))
        sleep(breakL)



    def getData(self):
    
        print ("stromStatus")

        #######################################################################################################################

        def enabled_disabled_converter(argument):
            switcher = {
                0: 'Disabled',
                1: 'Enabled',
            }
            return switcher.get(argument, 'nothing')

        def weekday_converter(argument):
            switcher = {
                1: 'Monday',
                2: 'Tuesday',
                3: 'Wednesday',
                4: 'Thursday',
                5: 'Friday',
                6: 'Saturday',
                7: 'Sunday',
            }
            return switcher.get(argument, 'nothing')

        def strompi_mode_converter(argument):
            switcher = {
                1: 'mUSB -> Wide',
                2: 'Wide -> mUSB',
                3: 'mUSB -> Battery',
                4: 'Wide -> Battery',
                5: "mUSB -> Wide -> Battery",
                6: "Wide -> mUSB -> Battery",
            }
            return switcher.get(argument, 'nothing')

        def alarm_mode_converter(argument):
            switcher = {
                1: 'Time-Alarm',
                2: 'Date-Alarm',
                3: 'Weekday-Alarm',
            }
            return switcher.get(argument, 'nothing')

        def batterylevel_shutdown_converter(argument):
            switcher = {
                0: 'Disabled',
                1: '10%',
                2: '25%',
                3: '50%',
            }
            return switcher.get(argument, 'nothing')

        def output_status_converter(argument):
            switcher = {
                0: 'Power-Off', #only for Debugging-Purposes
                1: 'mUSB',
                2: 'Wide',
                3: 'Battery',
            }
            return switcher.get(argument, 'nothing')


        def batterylevel_converter(batterylevel,charging):

            if charging:
                switcher = {
                    1: ' [10%] [charging]',
                    2: ' [25%] [charging]',
                    3: ' [50%] [charging]',
                    4: ' [100%] [charging]',
                }
                return switcher.get(batterylevel, 'nothing')
            else:
                switcher = {
                    1: ' [10%]',
                    2: ' [25%]',
                    3: ' [50%]',
                    4: ' [100%]',
                }
                return switcher.get(batterylevel, 'nothing')

        #######################################################################################################################
        
        wide_range_volt_min = 4.8
        battery_volt_min = 0.5
        mUSB_volt_min = 4.1

        breakS = 0.1
        breakL = 0.5

        # serial_port = serial.Serial()

        # serial_port.baudrate = 38400
        # serial_port.port = '/dev/serial0'
        # serial_port.timeout = 1
        # serial_port.bytesize = 8
        # serial_port.stopbits = 1
        # serial_port.parity = serial.PARITY_NONE
    
        # if serial_port.isOpen(): serial_port.close()
        # serial_port.open()
    
        writeSlow('quit')
        sleep(breakS)
        writeSlow('\x0D')
        sleep(breakL)

        writeSlow('status-rpi')
        sleep(1)
        writeSlow('\x0D')
        

        sp3_time = self.serial_port.readline(9999);
        sp3_date = self.serial_port.readline(9999);
        sp3_weekday = self.serial_port.readline(9999);
        sp3_modus = self.serial_port.readline(9999);
        sp3_alarm_enable = self.serial_port.readline(9999);
        sp3_alarm_mode = self.serial_port.readline(9999);
        sp3_alarm_hour = self.serial_port.readline(9999);
        sp3_alarm_min = self.serial_port.readline(9999);
        sp3_alarm_day = self.serial_port.readline(9999);
        sp3_alarm_month = self.serial_port.readline(9999);
        sp3_alarm_weekday = self.serial_port.readline(9999);
        sp3_alarmPoweroff = self.serial_port.readline(9999);
        sp3_alarm_hour_off = self.serial_port.readline(9999);
        sp3_alarm_min_off = self.serial_port.readline(9999);
        sp3_shutdown_enable = self.serial_port.readline(9999);
        sp3_shutdown_time = self.serial_port.readline(9999);
        sp3_warning_enable = self.serial_port.readline(9999);
        sp3_serialLessMode = self.serial_port.readline(9999);
        sp3_intervalAlarm = self.serial_port.readline(9999);
        sp3_intervalAlarmOnTime = self.serial_port.readline(9999);
        sp3_intervalAlarmOffTime = self.serial_port.readline(9999);
        sp3_batLevel_shutdown = self.serial_port.readline(9999);
        sp3_batLevel = self.serial_port.readline(9999);
        sp3_charging = self.serial_port.readline(9999);
        sp3_powerOnButton_enable = self.serial_port.readline(9999);
        sp3_powerOnButton_time = self.serial_port.readline(9999);
        sp3_poweroffMode = self.serial_port.readline(9999);
        sp3_powersave_enable = self.serial_port.readline(9999);
        sp3_ADC_Wide = float(self.serial_port.readline(9999))/1000;
        sp3_ADC_BAT = float(self.serial_port.readline(9999))/1000;
        sp3_ADC_USB = float(self.serial_port.readline(9999))/1000;
        sp3_ADC_OUTPUT = float(self.serial_port.readline(9999))/1000;
        sp3_output_status = self.serial_port.readline(9999);
        sp3_powerfailure_counter = self.serial_port.readline(9999);
        sp3_firmwareVersion = self.serial_port.readline(9999);

        date = int(sp3_date)

        strompi_year = int(sp3_date) // 10000
        strompi_month = int(sp3_date) % 10000 // 100
        strompi_day = int(sp3_date) % 100

        strompi_hour = int(sp3_time) // 10000
        strompi_min = int(sp3_time) % 10000 // 100
        strompi_sec = int(sp3_time) % 100

        try:
            if sp3_ADC_Wide > wide_range_volt_min:
                wide_range_volt = str(sp3_ADC_Wide) + 'V'
            else:
                wide_range_volt = ' not connected'

            if sp3_ADC_BAT > battery_volt_min:
                battery_volt = str(sp3_ADC_BAT) + 'V' + batterylevel_converter(int(sp3_batLevel),int(sp3_charging))
            else:
                battery_volt = ' not connected'

            if sp3_ADC_USB > mUSB_volt_min:
                microUSB_volt = str(sp3_ADC_USB) + 'V'
            else:
                microUSB_volt = ' not connected'

            self.output_volt = str(sp3_ADC_OUTPUT) + 'V'

            print(' ')
            print('---------------------------------')
            print('StromPi-Status:')
            print('---------------------------------')
            print('Time: ' + str(strompi_hour).zfill(2) + ':' + str(strompi_min).zfill(2) + ':' + str(strompi_sec).zfill(2))
            print('Date: ' + weekday_converter(int(sp3_weekday)) + ' ' + str(strompi_day).zfill(2) + '.' + str(strompi_month).zfill(2) + '.' + str(strompi_year).zfill(2))
            print(' ')

            print(' ')
            print('StromPi-Mode: ' + strompi_mode_converter((int(sp3_modus))))
            print(' ')
            print('Raspberry Pi Shutdown: ' + enabled_disabled_converter(int(sp3_shutdown_enable)))
            #print(' Shutdown-Timer: ' + str(sp3_shutdown_time).rstrip('\n').zfill(2) + ' seconds')
            print(' Shutdown-Timer: ' + str(sp3_shutdown_time).rstrip('\n').zfill(2) + ' seconds')
            print(' ')
            print('Powerfail Warning: ' + enabled_disabled_converter(int(sp3_warning_enable)))
            print(' ')

            print('Power Save Mode: ' + enabled_disabled_converter(int(sp3_powersave_enable)))
            print(' ')
            print('PowerOff Mode: ' + enabled_disabled_converter(int(sp3_poweroffMode)))
            print(' ')
            print('PowerOn-Button: ' + enabled_disabled_converter(int(sp3_powerOnButton_enable)))
            print(' ')
            print(' PowerOn-Button-Timer: ' + str(sp3_powerOnButton_time).rstrip('\n').zfill(2) + ' seconds')
            print(' ')
            print('Battery-Level Shutdown: ' + batterylevel_shutdown_converter(int(sp3_batLevel_shutdown)))
            print(' ')

            
            print('---------------------------------')
            print('Alarm-Configuration:')
            print('---------------------------------')
            print('WakeUp-Alarm: ' + enabled_disabled_converter(int(sp3_alarm_enable)))
            print(' Alarm-Mode: ' + alarm_mode_converter(int(sp3_alarm_mode)))
            print(' Alarm-Time: ' + str(sp3_alarm_hour).rstrip('\n').zfill(2) + ':' + str(sp3_alarm_min).rstrip('\n').zfill(2))
            print(' Alarm-Date: ' + str(sp3_alarm_day).rstrip('\n').zfill(2) + '.' + str(sp3_alarm_month).rstrip('\n').zfill(2))
            print(' WakeUp-Alarm: ' + weekday_converter(int(sp3_alarm_weekday)))
            print(' ')
            print('PowerOff-Alarm: ' + enabled_disabled_converter(int(sp3_alarmPoweroff)))
            print(' PowerOff-Alarm-Time: ' + str(sp3_alarm_hour_off).rstrip('\n').zfill(2) + ':' + str(sp3_alarm_min_off).rstrip('\n').zfill(2))
            print(' ')
            print('Interval-Alarm: ' + enabled_disabled_converter(int(sp3_intervalAlarm)))
            print(' Interval-On-Time: ' + str(sp3_intervalAlarmOnTime).rstrip('\n').zfill(2) + ' minutes')
            print(' Interval-Off-Time: ' + str(sp3_intervalAlarmOffTime).rstrip('\n').zfill(2) + ' minutes')
            print(' ')
            print('---------------------------------')
            print('Voltage-Levels:')
            print('---------------------------------')
            print('Wide-Range-Inputvoltage: ' + wide_range_volt)
            print('LifePo4-Batteryvoltage: ' + battery_volt)
            print('microUSB-Inputvoltage: ' + microUSB_volt)
            print('Output-Voltage: ' + self.output_volt)
            print(' ')

        except KeyboardInterrupt:
            print('interrupted!')
            

        self.serial_port.close()
        
    def __init__(self):

        self.getData()
        
        
