#!/usr/bin/python

import pickle
import socket
import sys

# Total packet size is 32 bytes.
BUFFER_SIZE = 32

"""
recvall()
  Params:
    sock - a socket object instantiated via socket.socket().
  Returns:
    The data received from the server.
  Description:
    Helper function that calls socket.recv() multiple times until all the data
    from the server is received.
"""
def recvall( sock ):
    data = ''

    while True:
        # Receive a packet
        packet = sock.recv( BUFFER_SIZE )
        data  += packet

        if len( packet ) < BUFFER_SIZE:
            # If the packet is smaller than the max packet size, we received
            # the last packet
            break

    return data

"""
Script Usage
"""
def usage():
    print 'Usage: ./smsclientTCP.py <IP address> <port> <message file>'
    exit( 0 )

"""
Script Main
"""
def main( argv ):
    # Parse arguments
    if len( argv ) != 3:
        usage()

    ip_address   = argv[0]
    port         = int( argv[1] )
    message_file = argv[2]

    # Get the message we want to send from the file that was passed in
    message_handle = open( message_file, 'r' )
    message        = message_handle.read()

    # Create a TCP socket via the internet
    sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )

    # Connect to the IP and port that were passed in
    sock.connect( ( ip_address, port ) )

    # Encode the message
    message_data = pickle.dumps( message )

    # Send the encoded message to the server
    sock.sendall( message_data )

    # Receive the encoded message stats from the server
    response = recvall( sock )

    # Decode the message stats
    ( score, total_count, suspicious_words ) = pickle.loads( response )
    print 'Response from server:\n{0} {1} {2}'.format( score, total_count, ' '.join( suspicious_words ) )

    # Close the connection
    sock.close()

if __name__ == "__main__":
    main( sys.argv[1:] )

sys.exit( 0 )
