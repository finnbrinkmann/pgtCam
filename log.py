import os


# this function replaces the print function, so all output is written to console, monitor and logfile

def log(s):

    try:
        s = str(s)
        print(s)
    except:
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
    except:
        print ("ERROR: Could not open file: /dev/tty1")


    try:
        f = open('/media/stick/log.txt', 'a')
        f.write(s + '\n')
        f.close()
    except:
        print ("ERROR: Could not open file: /media/stick/log.txt")
        
        

def logAkku(s):

    try:
        s = str(s)
        print("Akkuspannung: " + s + "V")
    except:
        print("Error: Can not cast log data to string")
                
    try:
        f = open('/dev/tty1', 'w')
        f.write(s + 'V\n')
        f.close()
    except:
        print ("ERROR: Could not open file: /dev/tty1")

    try:
        f = open('/media/stick/logAkku.txt', 'a')
        f.write(s + '\n')
        f.close()
    except:
        print ("ERROR: Could not open file: /media/stick/logAkku.txt")
        
