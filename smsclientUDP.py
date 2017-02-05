#!/usr/bin/python

import pickle
import socket
import sys

BUFFER_SIZE         = 32
BUFFER_PAYLOAD_SIZE = BUFFER_SIZE - 5


def receive_score_data( sock ):
    global score
    global total_count
    global suspicious_words

    while True:
        ( data, server_addr ) = sock.recvfrom( BUFFER_SIZE )

        if data == '\0':
            break
        elif data.startswith( 'S:' ):
            score = float( data[ 2: ] )

            if score == 0:
                score = 0

        elif data.startswith( 'T:' ):
            total_count = int( data[ 2: ] )
        else:
            suspicious_words.append( data )

def send_message( sock ):
    global message

    message_parts = [
        str( i / BUFFER_PAYLOAD_SIZE ) + ':' + message[ i : i + BUFFER_PAYLOAD_SIZE ]
        for i in range(
            0,
            len( message ),
            BUFFER_PAYLOAD_SIZE
        )
    ]

    packet_number = 0

    for message_part in message_parts:
        sock.sendto( message_part, ( ip_address, port ) )

    sock.sendto( '\0', ( ip_address, port ) )

def usage():
    print 'Usage: ./smsclientUDP.py <IP address> <port> <message file>'
    exit( 0 )

def main( argv ):
    global message, ip_address, port
    global score, total_count, suspicious_words

    if len( argv ) != 3:
        usage()

    ip_address   = argv[0]
    port         = int( argv[1] )
    message_file = argv[2]

    message_handle = open( message_file, 'r' )
    message        = message_handle.read()

    sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
    sock.settimeout( 2 )

    suspicious_words = []
    try_count        = 0

    while try_count < 3:
        try:
            send_message( sock )
            receive_score_data( sock )
            print 'Response from server:\n{0} {1} {2}'.format( score, total_count, ' '.join( suspicious_words ) )
            break
        except socket.timeout:
            print 'The server has not answered in the last two seconds.\nretrying...'
            try_count += 1

    if try_count >= 3:
        print 'Server did not respond after three attempts.'

    sock.close()

if __name__ == "__main__":
    main( sys.argv[1:] )

sys.exit( 0 )
