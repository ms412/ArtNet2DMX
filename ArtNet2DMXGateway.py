#!/usr/bin/python3

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

__app__ = "ArtNet2DMX-Gateway"
__VERSION__ = "0.8"
__DATE__ = "01.12.2020"
__author__ = "Markus Schiesser"
__contact__ = "M.Schiesser@gmail.com"



import sys
import logging
from configobj import ConfigObj
from library.DMXSerial import DMXSerial
from library.ArtNetServer import ArtNet
from library.logger import loghandler


class ArtNet2DMXGateway(object):
    def __init__(self, config):

        self._configfile = config
        self._log = None

        self._dmxDataStore = [0] * 512

    def readconfig(self):
        _config = ConfigObj(self._configfile)

        if bool(_config) is False:
            print('ERROR config file not found', self._configfile)
            sys.exit()

        self._config_log = _config.get('LOGGING', None)
        self._configServer = _config.get('SERVER',None)

        return True

    def startLogger(self):
        self._root_logger = loghandler(self._config_log.get('NAME','ArtNet2DMX'))
        self._root_logger.handle(self._config_log.get('LOGMODE','PRINT'),self._config_log)
        self._root_logger.level(self._config_log.get('LOGLEVEL','DEBUG'))
        self._rootLoggerName = self._config_log.get('NAME', 'ArtNet2DMX')
        self._log = logging.getLogger(self._rootLoggerName + '.' + self.__class__.__name__)
        return True

    def startServer(self):
        _type = self._configServer.get('TYPE','ArtNet')
        _host = self._configServer.get('HOST','localhost')
       # print(self._configServer.get('PORT',9020),type(self._configServer.get('PORT',9020)))

        _port = int(self._configServer.get('PORT',9020))

      #  module = __import__(DMXServer)
       # class_ = getattr(module, _type)
        self._server = ArtNet(_host,_port,self.callback,self._rootLoggerName)

    def startSerial(self):
        _serial = self._configServer.get('SERIAL','/dev/ttyUSB0')
        self._serial = DMXSerial(_serial,self._rootLoggerName)

    def callback(self,dmxData):
        #print('callback', dmxData)

        _mode = self._configServer.get('MODE','THROUGH')

        _lenght = len(dmxData)
        _temp = self._dmxDataStore.copy()
        # print('compare',_lenght,dmxData)
        self._dmxDataStore[0:_lenght] = dmxData

        # print('Store',self._dmxDataStore)
        # print('temp ', _temp)

        if _mode in 'THROUGH':
            self._serial.send(self._dmxDataStore)

        else:
            if self._dmxDataStore != _temp:
                self._serial.send(self._dmxDataStore)

    def run(self):
        self.readconfig()
        self.startLogger()
        self._log.info('Start Application: %s %s %s' % (__app__, __VERSION__, __DATE__))
        self.startSerial()
        self.startServer()



if __name__ == "__main__":
    gw =  ArtNet2DMXGateway('/opt/ArtNet2DMX/ArtNet2DMXGateway.cfg')
    gw.run()
