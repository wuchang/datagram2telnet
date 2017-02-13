# coding:utf-8


from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor, task
import logging
import logging.handlers

def getUDPlogger():
    logger = logging.getLogger( __name__ )
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
  
    h2 = logging.handlers.DatagramHandler('127.0.0.1',2046)
    h2.setFormatter(h2)

    logger.addHandler(h2)
    logger.setLevel(logging.DEBUG)
    return logger

 
def runlogger():
    import socket  
    import time
 
    counter=0
    udplogger = getUDPlogger();
    while True:  
        counter += 1  
        udplogger.info('auto logger.... {0}'.format(counter))     
        #time.sleep(0.1)

if __name__=="__main__" :
    runlogger()