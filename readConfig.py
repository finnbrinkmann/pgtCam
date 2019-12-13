# read config file and write data to strompi on seriel interface
from datetime import datetime
from log import log as log

def readConfig():

    startStr = "01.01.190000:00"
    endStr = "01.01.190000:00"
    
    log ("readConfig")
    filename = "config.txt"
    file = open(filename, 'r')

    startTime  = []
    endTime = []
    

    for line in file:
    
        log (line)
        #log (type(line))
        line = line.replace(" ","") #remove spaces tabs and newlines
        line = line.replace("\t","")
        line = line.replace("\n","")
        #log (len(line))
        
        if len(line)> 0 :
            if line[0] == "#":#skip if it is a comment
                continue
            elif line.strip():    

                data = line.split("=")
                log(data)
                
                if data[0] == "on":
                    log ("on is true")
                    startTime.append( datetime.strptime(data[1], "%d.%m.%Y%H:%M")) #create vector of boot times
                    
                elif data[0] == "off":
                    log ("off is true")
                    endTime.append( datetime.strptime(data[1], "%d.%m.%Y%H:%M")) #create vector of shutdown times



    log ("länge" + str(len(startTime)))
    
    startTime.sort()# earlyest date at first
    
    for times in startTime:
       
        log (str(times.day) + " " + str(times.month) + " " + str(times.year) + " " + str(times.hour) + " " + str(times.minute ))

        if times < datetime.now():
            log ("Warning: Start liegt in der Vergangenheit")
        else:
            #programm strom pi on this date

log ("start")
readConfig()
log("end")