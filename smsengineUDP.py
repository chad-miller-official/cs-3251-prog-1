#!/usr/bin/python

from __future__ import division

import pickle
import socket
import sys

import time

BACKLOG_QUEUE_SIZE = 5
BUFFER_SIZE        = 32
BAD_INPUT_ERROR    = ( 0, -1, [ 'ERROR' ] )

def recvall( sock ):
    data_parts = {}

    while True:
        ( packet, addr ) = sock.recvfrom( BUFFER_SIZE )

        if packet == '\0':
            break

        packet_parts   = packet.split( ':', 1 )
        packet_number  = int( packet_parts[0] )
        packet_message = packet_parts[1]

        data_parts[ packet_number ] = packet_message

    data = ''

    for i in sorted( data_parts.keys() ):
        data += data_parts[i]

    return ( data, addr )

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
    print 'Usage: ./smsengineUDP.py <port> <suspicious words file>'
    exit( 0 )

def main( argv ):
    global words_list

    if len( argv ) != 2:
        usage()

    port       = int( argv[0] )
    words_file = argv[1]
    ip_address = socket.gethostbyname( socket.gethostname() )

    words_handle = open( words_file, 'r' )
    words        = words_handle.read()
    words_list   = words.split( '\n' )

    sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
    sock.bind( ( ip_address, port ) )

    print '({0}) Listening on port {1}.'.format( ip_address, port )

    while True:
        try:
            ( message, addr ) = recvall( sock )
            client_address    = addr[0]
            client_port       = addr[1]

            ( score, total_count, suspicious_words ) = calculate_score( message )

            sock.sendto( 'S:' + str( score ),       ( client_address, client_port ) )

            time.sleep( 5 )

            sock.sendto( 'T:' + str( total_count ), ( client_address, client_port ) )

            for suspicious_word in suspicious_words:
                sock.sendto( suspicious_word, ( client_address, client_port ) )

            sock.sendto( '\0', ( client_address, client_port ) )
        except KeyboardInterrupt:
            break

    print '\nExiting...'
    sock.close()

if __name__ == "__main__":
    main( sys.argv[1:] )

sys.exit( 0 )
