import os


# this function replaces the print function, so all output is written to console, monitor and logfile

def log(s):

    
    paths = ["/media/ntfs/","/media/vFat/","/media/exFat/"]

    try:
        s = str(s)
        print(s)
    except Exception as e:
        s = "Error: Can not cast log data to string"
        print(s)
                
    try:
        f = open('/dev/tty1', 'w')
        pointer = 0
        
        while pointer < len(s):
            if pointer == 0:
                f.write(s[pointer:pointer + 40] + '\n')
                pointer = pointer + 40
                
            else:
                f.write('    ' + s[pointer:pointer + 40 - 4] + '\n') #write tab in front of 2nd line. write less following chars
                pointer = pointer + 40 - 4
            
        f.close()
    except Exception as e:
        print ("ERROR: Could not open file: /dev/tty1 " + str(e))

    for x in paths:
        if os.path.ismount(x):

            try:
                f = open(x + 'log.txt', 'a')
                f.write(s + '\n')
                f.close()
            except Exception as e:
                print ("ERROR: Could not open file: " + x + "log.txt " + str(e))
                
            

def logAkku(s):

    paths = ["/media/ntfs/","/media/vFat/","/media/exFat/"]

    try:
        s = str(s)
        print("Akkuspannung: " + s + "V")
    except Exception as e:
        print("Error: Can not cast log data to string " + str(e))
                
    try:
        f = open('/dev/tty1', 'w')
        f.write(s + 'V\n')
        f.close()
    except Exception as e:
        print ("ERROR: Could not open file: /dev/tty1 " + str(e))

    for x in paths:
        if os.path.ismount(x):
            try:
                f = open(x + 'akkuLog.txt', 'a')
                f.write(s + '\n')
                f.close()
            except Exception as e:
                print ("ERROR: Could not open file: " + x + "akkuLog.txt " + str(e))
        
