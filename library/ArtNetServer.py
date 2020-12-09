#!/usr/bin/python3

__app__ = "ArtNet-Server"
__VERSION__ = "0.8"
__DATE__ = "01.12.2020"
__author__ = "Markus Schiesser"
__contact__ = "M.Schiesser@gmail.com"

import os
import socket
import threading
import logging


class Lib485(object):
    def __init__(self, host='localhost',port=9020,callback=None,logger=None):

        _libName = str(__name__.rsplit('.', 1)[-1])
        self._log = logging.getLogger(logger + '.' + _libName + '.' + self.__class__.__name__)

        self._log.debug('Create Server Object')
        print(self._log)

        self._host = host
        self._port = port
        self._callback = callback
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((self._host, self._port))

        self.listen()

    def listen(self):
        self._sock.listen()
        while True:
            client, address = self._sock.accept()
            client.settimeout(60)
            threading.Thread(target = self.listenToClient,args = (client,address)).start()

    def listenToClient(self, client, address):
        self._log.info('Connected by', address)
        size = 1024
        while True:
            try:
                data = client.recv(size)
                if data:
                    # Set the response to echo back the recieved data
                    self._log.debug('Received Data', list(data))
                    self._callback((data))
                else:
                    self._log.error('Connected by', address)
            except:
                self._log.error('Connected Clossed by Client', address)
                client.close()
                return False

class ArtNet(object):
    def __init__(self, host='localhost',port=6465,callback=None,logger=None):

        _libName = str(__name__.rsplit('.', 1)[-1])
        self._log = logging.getLogger(logger + '.' + _libName + '.' + self.__class__.__name__)

        self._log.debug('Create Server Object')

        self._host = host
        self._port = port
        self._callback = callback
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((self._host, self._port))

        self.listen()

    def listen(self):
         while True:

            data = self._sock.recv(10240)


            if len(data) < 20:
                continue

            if data[0:7] != b"Art-Net" or data[7] != 0:
                # artnet package
                continue

            if data[8] != 0x00 or data[9] != 0x50:
                # OpDmx
                continue

            protverhi = data[10]
            protverlo = data[11]
            sequence = data[12]
            physical = data[13]
            subuni = data[14]
            net = data[15]
            lengthhi = data[16]
            length = data[17]
          #  print(length)
            dmx = data[18:]

            self._log.debug('ArtNet Frame recieved lenght: %d, data: %s', length,dmx)
            self._callback(dmx)



class callbackTest(object):

    def callme(self,data):
        print('Callmeback',data)


if __name__ == "__main__":

    x = callbackTest()
    server = ArtNet('192.168.2.119',6454,x.callme)
    server.listen()
