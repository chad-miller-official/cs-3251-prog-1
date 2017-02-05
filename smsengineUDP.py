#!/usr/bin/python

from __future__ import division

import socket
import sys

# Total packet size is 32 bytes.
BUFFER_SIZE = 32

# In the event of bad input from the client, this data blob is sent back.
BAD_INPUT_ERROR = ( 0, -1, [ 'ERROR' ] )

"""
recvall()
  Params:
    sock - a socket object instantiated via socket.socket().
  Returns:
    a tuple with all the data received in the first position and the client
    IP address/port in the second position.
  Description:
    Helper function that calls socket.recv() multiple times until all the data
    from the client is received. When a packet containing only the null
    character is received, we stop calling recv(), and then we assemble the
    data and return it.
"""
def recvall( sock ):
    # Data parts is a hash that maps integer indexes to packet payloads. A dict
    # is used instead of a list because if packets are received out of order and
    # we receive, for example, packet 3 before packet 2, trying to index 3 into
    # a list before indexing 2 will result in an exception being thrown.
    data_parts = {}

    while True:
        # Receive a packet
        ( packet, addr ) = sock.recvfrom( BUFFER_SIZE )

        if packet == '\0':
            # If the packet is just the null character, we're done receiving
            # packets so break out of the loop
            break

        # Separate the header from the payload
        packet_parts   = packet.split( ':', 1 )

        # The header is just the packet number
        packet_number  = int( packet_parts[0] )

        # The payload is the message chunk
        packet_message = packet_parts[1]

        # Associate the packet number with the message chunk
        data_parts[ packet_number ] = packet_message

    data = ''

    # Finally, order the dict keys and assemble the full message
    for i in sorted( data_parts.keys() ):
        data += data_parts[i]

    return ( data, addr )

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

    if( char_count <= 0 or char_count > 1000 ):
        # If the message was empty or had more than 1000 characters, return
        # the bad input blob
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
    print 'Usage: ./smsengineUDP.py <port> <suspicious words file>'
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

    # Create a datagram socket via the internet
    sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )

    # Bind the socket to the port that was passed in
    sock.bind( ( ip_address, port ) )
    print '({0}) Listening on port {1}.'.format( ip_address, port )

    while True:
        try:
            # Receive data from the client
            ( message, addr ) = recvall( sock )
            client_address    = addr[0]
            client_port       = addr[1]

            # Calculate the message stats
            ( score, total_count, suspicious_words ) = calculate_score( message )

            # Send the score with 'S:' as the header
            sock.sendto( 'S:' + str( score ), ( client_address, client_port ) )

            # Send the total count with 'T:' as the header
            sock.sendto( 'T:' + str( total_count ), ( client_address, client_port ) )

            # Send each suspicious word we found in the message as its own
            # packet
            for suspicious_word in suspicious_words:
                sock.sendto( suspicious_word, ( client_address, client_port ) )

            # Send a null character packet to let the client know we're done
            # sending data
            sock.sendto( '\0', ( client_address, client_port ) )
        except KeyboardInterrupt:
            # If someone Ctrl+C's the server, gracefully exit
            break

    print '\nExiting...'
    sock.close()

if __name__ == "__main__":
    main( sys.argv[1:] )

sys.exit( 0 )
