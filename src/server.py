# coding:utf-8

from twisted.protocols import basic
from twisted.internet import protocol
from twisted.application import service, internet
from twisted.internet import reactor
import logging
import struct
import pickle
import json


def getLogger(name=__name__):
    logger = logging.getLogger( name )
    handler = logging.StreamHandler()    
    handler.setFormatter( getLoggingFormatter() )
    logger.addHandler(handler)
  
    logger.setLevel(logging.DEBUG)
    return logger

def getLoggingFormatter():
    return logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')

class UdpServerProtocol(protocol.DatagramProtocol):
    logger = getLogger('UdpServerProtocol')
    loggingFormatter = getLoggingFormatter()
    def __init__(self,distributer, *args):
        super(UdpServerProtocol, self).__init__(*args)
        self.distributer = distributer
        

    def datagramReceived(self, data, addr):
        slen = struct.unpack('>L', data[:4])[0]
        self.logger.debug('recv from:{0},datalen:{1},datatype:{2},slen:{3}'.format(addr, len(data), type(data),slen ))
        chunk = data[4:slen+4]
        try:
            obj = pickle.loads(chunk)
            record = logging.makeLogRecord(obj)
            msg = self.loggingFormatter.format(record)
            jsonstr = msg+'\r\n'
            self.distributer.distribute( jsonstr.encode('utf-8') )
            self.logger.debug('recv log:{0}'.format(jsonstr))
        except Exception as ex:
            self.logger.error('UDP: invalid data to pickle %s,%s', chunk,ex)

        

class TelnetServerProtocol(protocol.Protocol):
    logger = getLogger('TelnetServerProtocol')
    def __init__(self, *args):
        super(TelnetServerProtocol, self).__init__(*args)

    def connectionMade(self):
        self.factory.clients.append(self)
        self.logger.info("Got new client from:{0}, now total clients:{1}"
            .format(self.transport.client, len(self.factory.clients)))
        self.transport.write( 'welcome!'.encode('utf-8'))

    def connectionLost(self, reason):
        self.factory.clients.remove(self)        
        self.logger.info("Lost a client!reason:{0},from:{1}, now total clients:{2}"
            .format(reason, self.transport.client, len(self.factory.clients)))

    def sendData(self,data):
        self.transport.write( data)


class TelnetFactory(protocol.ServerFactory):
    protocol = TelnetServerProtocol
    def __init__(self, *args):
        super(TelnetFactory, self).__init__(*args)
        self.clients=[]  
        self.logger = getLogger('TelnetFactory')

    def distribute(self,data):
        self.logger.debug('distribute to {0} clients,data:{1}'.format( len(self.clients), data))
        for c in self.clients:
            c.sendData( data )

def main(udpport,telnetport,udphost='0.0.0.0',telnethost='0.0.0.0'):
    logger = getLogger(__name__)
    tel = TelnetFactory()
    udp = UdpServerProtocol(tel)
    reactor.listenTCP(telnetport, tel)
    reactor.listenUDP(udpport, udp)
    logger.info('server running!  UDP:({0}:{1}) ,  Telnet:({2}:{3})'
        .format( udphost,udpport, telnethost,telnetport))
    reactor.run()

if __name__=="__main__":
    main(2046,2047)
