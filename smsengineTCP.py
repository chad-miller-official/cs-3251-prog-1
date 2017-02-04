#!/usr/bin/python

from __future__ import division

import pickle
import socket
import sys

BACKLOG_QUEUE_SIZE = 1
BUFFER_SIZE        = 256
BAD_INPUT_ERROR    = ( 0, -1, [ 'ERROR' ] )

def recvall( sock ):
    data = ''

    while True:
        packet = sock.recv( BUFFER_SIZE )
        data  += packet

        if len( packet ) < BUFFER_SIZE:
            break

    return data

def calculate_score( message ):
    global words_list

    suspicious_words = []
    message_tokens   = message.split()
    total_count      = len( message_tokens )

    if( total_count <= 0 or total_count > 1000 ):
        return BAD_INPUT_ERROR

    for token in message_tokens:
        if token.lower() in words_list:
            suspicious_words.append( token )

    score = len( suspicious_words )  / total_count

    return (
        score,
        total_count,
        suspicious_words
    )

def usage():
    print 'Usage: ./smsengineTCP.py <port> <suspicious words file>'
    exit( 0 )

def main( argv ):
    global words_list

    if len( argv ) != 2:
        usage()

    port       = int( argv[0] )
    words_file = argv[1]
    ip_address = '127.0.0.1'

    words_handle = open( words_file, 'r' )
    words        = words_handle.read()
    words_list   = words.split( '\n' )

    sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    sock.bind( ( ip_address, port ) )
    sock.listen( BACKLOG_QUEUE_SIZE )

    print 'Listening on port {}.'.format( port )

    while True:
        try:
            ( client_sock, address ) = sock.accept()

            message      = recvall( client_sock )
            message_data = pickle.loads( message )

            score_data = calculate_score( message_data )

            client_sock.sendall( pickle.dumps( score_data ) )
            client_sock.close()
        except KeyboardInterrupt:
            break

    print '\nExiting...'
    sock.close()

if __name__ == "__main__":
    main( sys.argv[1:] )

sys.exit( 0 )
