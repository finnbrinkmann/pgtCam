# log2.py

import logging
from logging.handlers import RotatingFileHandler
import os
import sys


paths = ["/media/ntfs/","/media/vFat/","/media/exFat/"]
#tty = os.ttyname(sys.stdout.fileno())

# Create a custom logger
logger = logging.getLogger(__name__)

akkuLogger = logging.getLogger(__name__)


# Create handlers
c_handler = logging.StreamHandler()
sd_handler = RotatingFileHandler('log/sdcard.log',maxBytes=1024*1024*5, backupCount=2)

akku_handler = RotatingFileHandler('log/akku.log',maxBytes=1024*1024*5, backupCount=2)
#tty_handler = logging.FileHandler(tty)
tty_handler = logging.StreamHandler(sys.stdout)

#for x in paths:
#    if os.path.ismount(x):
#        usb_handler = logging.FileHandler(x + 'log.txt')
#        print(x + 'handler created')



c_handler.setLevel(logging.DEBUG)
sd_handler.setLevel(logging.DEBUG)
#usb_handler.setLevel(logging.DEBUG)
tty_handler.setLevel(logging.INFO)

akku_handler.setLevel(logging.INFO)


# Create formatters and add it to handlers
c_format = logging.Formatter('%(levelname)s: %(message)s')
#c_format = logging.Formatter('%(message)s')
#c_format = logging.Formatter('%(message)s')
sd_format = logging.Formatter('%(asctime)s|%(levelname)s\t%(message)s')
#usb_format = logging.Formatter('%(asctime)s|%(levelname)s\t%(message)s')
#f_format = logging.Formatter('%(asctime)s|%(message)s')
tty_format = logging.Formatter('%(levelname)s: %(message)s')

akku_format = logging.Formatter('%(asctime)s;%(message)s')

c_handler.setFormatter(c_format)
sd_handler.setFormatter(sd_format)
#usb_handler.setFormatter(usb_format)
tty_handler.setFormatter(tty_format)

akku_handler.setFormatter(akku_format)

# Add handlers to the logger
logger.addHandler(c_handler)
logger.addHandler(sd_handler)
#logger.addHandler(usb_handler)
logger.addHandler(tty_handler)

akkuLogger.addHandler(akku_handler)

logging.raiseExceptions = False#ignore exceptions e.g. if usb is removed

logger.setLevel(logging.DEBUG)
akkuLogger.setLevel(logging.INFO)
#to test the logger

#logger.debug('This is an debug')
#logger.info('This is an info')
#logger.warning('This is a warning')
#logger.error('This is an error')






