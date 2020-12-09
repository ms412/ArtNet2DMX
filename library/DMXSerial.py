#!/usr/bin/python3


__app__ = "DMX-Serial"
__VERSION__ = "0.8"
__DATE__ = "01.12.2020"
__author__ = "Markus Schiesser"
__contact__ = "M.Schiesser@gmail.com"


import serial
import time
import os
import logging

module_logger = logging.getLogger('ArtNet2DMXGateway.__app__')


if os.name == "posix":
    import fcntl

class DMXSerial(object):
    def __init__(self, port="/dev/ttyUSB0",logger = None):

        _libName = str(__name__.rsplit('.', 1)[-1])
        self._log = logging.getLogger(logger + '.' + _libName + '.' + self.__class__.__name__)

        self._log.debug('Create Server Object')

        self._serial = serial.Serial(port)
        self._serial.baudrate = 250000
        self._serial.bytesize = serial.EIGHTBITS
        self._serial.parity = serial.PARITY_NONE
        self._serial.stopbits = serial.STOPBITS_TWO
        self._serial.xonoff = False

        self._dmxDataStore = [0]*512
        self.data = [0]*512
        self.nextdata = [0]*512
        self.newdata = False


    def send(self, data):

        fcntl.ioctl(self._serial, 0x5427)  # Yeah, it's magic. Start Break (TIOCSBRK)
        time.sleep(0.0001)
        fcntl.ioctl(self._serial, 0x5428)  # Yeah, it's magic. End Break (TIOCCBRK)
        self._serial.write(bytes((0,)))
        self._serial.write(bytes(data))
        self._log.debug('DMX Write Data %s',list(data))
      #  print('Serial',list(data))
        self._serial.flush()

    def compare(self,dmxData):

        _lenght = len(dmxData)
        _temp = self._dmxDataStore.copy()
        #print('compare',_lenght,dmxData)
        self._dmxDataStore[0:_lenght] = dmxData

       # print('Store',self._dmxDataStore)
        #print('temp ', _temp)

        if self._dmxDataStore != _temp:
          #  print('diff')
            self.sender2()

if __name__ == "__main__":

    x = SerialDMX()
    x.startServer()