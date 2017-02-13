#!/usr/bin/python

from __future__ import division

import pickle
import socket
import sys

# The maximum number of queued connections the server will allow.
BACKLOG_QUEUE_SIZE = 5

# Total packet size is 32 bytes.
BUFFER_SIZE = 32

# In the event of bad input from the client, this data blob is sent back.
BAD_INPUT_ERROR = ( 0, -1, [ 'ERROR' ] )

"""
recvall()
  Params:
    sock - a socket object instantiated via socket.socket().
  Returns:
    The data received from the client.
  Description:
    Helper function that calls socket.recv() multiple times until all the data
    from the client is received.
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
calculate_score()
  Params:
    message - the message that was received from the client.
  Returns:
    a tuple containing the spam score in the first index, the total word count
    in the second index, and the list of suspicious words that were found in the
    message in the third index.
  Description:
    Calculate the client message's spam score, total word count, and assemble a
    list of all the suspicious words that were found in the message.
"""
def calculate_score( message ):
    global words_list

    suspicious_words = []
    char_count       = len( message )

    if char_count <= 0 or char_count > 1000:
        # If the message was empty or had more than 1000 characters, return
        # the bad input blob
        return BAD_INPUT_ERROR

    if not all( ord( char ) < 128 for char in message ):
        # If the message contains non-ASCII characters, return the bad input
        # blob
        return BAD_INPUT_ERROR

    total_count = 0

    # Add suspicious words found in the message to the suspicious words list,
    # and simultaneously count the number of tokens
    for token in message.split():
        total_count += 1

        if token.lower() in words_list:
            suspicious_words.append( token )

    # Calculate the spam score
    score = len( suspicious_words )  / total_count

    return (
        score,
        total_count,
        suspicious_words
    )

"""
Script Usage
"""
def usage():
    print 'Usage: ./smsengineTCP.py <port> <suspicious words file>'
    exit( 0 )

"""
Script Main
"""
def main( argv ):
    global words_list

    # Parse arguments
    if len( argv ) != 2:
        usage()

    port       = int( argv[0] )
    words_file = argv[1]
    ip_address = socket.gethostbyname( socket.gethostname() )

    # Get the list of suspicious words to look for in a client message
    words_handle = open( words_file, 'r' )
    words        = words_handle.read()
    words_list   = words.split( '\n' )

    # Create a TCP socket via the internet
    sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )

    # Bind the socket to the port that was passed in
    sock.bind( ( ip_address, port ) )

    # Let incoming connections be queued
    sock.listen( BACKLOG_QUEUE_SIZE )
    print '({0}) Listening on port {1}.'.format( ip_address, port )

    while True:
        try:
            # Accept a client connection
            ( client_sock, address ) = sock.accept()

            # Receive data from the client
            message = recvall( client_sock )

            # Decode client data
            message_data = pickle.loads( message )

            # Calculate message stats
            score_data = calculate_score( message_data )

            # Encode message stats and send it to the client
            client_sock.sendall( pickle.dumps( score_data ) )

            # Close the client connection
            client_sock.close()
        except KeyboardInterrupt:
            # If someone Ctrl+C's the server, gracefully exit
            break

    print '\nExiting...'
    sock.close()

if __name__ == "__main__":
    main( sys.argv[1:] )

sys.exit( 0 )
