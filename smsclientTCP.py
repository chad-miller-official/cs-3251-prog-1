#!/usr/bin/python

import pickle
import socket
import sys

BUFFER_SIZE = 256

def recvall( sock ):
    data = ''

    while True:
        packet = sock.recv( BUFFER_SIZE )
        data  += packet

        if len( packet ) < BUFFER_SIZE:
            break

    return data

def usage():
    print 'Usage: ./smsclientTCP.py <IP address> <port> <message file>'
    exit( 0 )

def main( argv ):
    if len( argv ) != 3:
        usage()

    ip_address   = argv[0]
    port         = int( argv[1] )
    message_file = argv[2]

    message_handle = open( message_file, 'r' )
    message        = message_handle.read()

    sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    sock.connect( ( ip_address, port ) )

    message_data = pickle.dumps( message )
    sock.sendall( message_data )

    response                                 = recvall( sock )
    ( score, total_count, suspicious_words ) = pickle.loads( response )

    print 'Response from server:\n{0} {1} {2}'.format( score, total_count, ' '.join( suspicious_words ) )

    sock.close()

if __name__ == "__main__":
    main( sys.argv[1:] )

sys.exit( 0 )
