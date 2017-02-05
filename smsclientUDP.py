#!/usr/bin/python

import socket
import sys

# Total packet size (including header and payload) is 32 bytes.
BUFFER_SIZE = 32

# Buffer header size is 5 bytes (an unsigned integer up to 4 bytes long and a
# header delimiter character); payload size is packet size minus header size
BUFFER_PAYLOAD_SIZE = BUFFER_SIZE - 5

"""
receive_score_data()
  Params:
    sock - a socket object instantiated via socket.socket().
  Returns:
    nothing.
  Description:
    Receives score data from the server. This includes:
     - Spam score
     - Total word count
     - List of suspicious words found in message
    These values are not returned. Rather, they are stored as global variables
    in case this function must be called multiple times to receive all values
    from the server.
"""
def receive_score_data( sock ):
    global score
    global total_count
    global suspicious_words

    while True:
        ( data, server_addr ) = sock.recvfrom( BUFFER_SIZE )

        if data == '\0':
            # A packet containing only the null character means we're done
            # receiving packets
            break
        elif data.startswith( 'S:' ):
            # A packet whose data begins with 'S:' means we're reciving a spam
            # score
            score = float( data[ 2: ] )

            if score == 0:
                # If the score is 0, make sure it shows up as 0 and not 0.0
                score = 0
        elif data.startswith( 'T:' ):
            # A packet whose data begins with 'T:' means we're receiving a total
            # word count
            total_count = int( data[ 2: ] )
        else:
            # A packet with no special header data means we're receiving a
            # suspicious word that was found
            suspicious_words.append( data )

"""
send_message()
  Params:
    sock - a socket object instantiated via socket.socke().
  Returns:
    nothing.
  Description:
    Sends the messaged that was passed into this script. It is first divided
    into multiple packets; each packet is given a header containing the packet
    number and then each packet is sent sequentially to the server. Finally,
    a null character terminating packet is sent to let the server know we're
    done sending it packets.
"""
def send_message( sock ):
    global message

    # Split the message up into parts and give each one a header too
    message_parts = [
        str( i / BUFFER_PAYLOAD_SIZE ) + ':' + message[ i : i + BUFFER_PAYLOAD_SIZE ]
        for i in range(
            0,
            len( message ),
            BUFFER_PAYLOAD_SIZE
        )
    ]

    # Send all the packets to the server, sequentially
    for message_part in message_parts:
        sock.sendto( message_part, ( ip_address, port ) )

    # Send a null character packet to the server to let it know we're done
    sock.sendto( '\0', ( ip_address, port ) )

"""
Script Usage
"""
def usage():
    print 'Usage: ./smsclientUDP.py <IP address> <port> <message file>'
    exit( 0 )

"""
Script Main
"""
def main( argv ):
    global message, ip_address, port
    global score, total_count, suspicious_words

    # Parse arguments
    if len( argv ) != 3:
        usage()

    ip_address   = argv[0]
    port         = int( argv[1] )
    message_file = argv[2]

    # Get the message we want to send from the file that was passed in
    message_handle = open( message_file, 'r' )
    message        = message_handle.read()

    # Create a datagram (UDP) socket via the internet
    sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )

    # Set the socket timeout to two seconds
    sock.settimeout( 2 )

    # Initialize the global suspicious words list populated in
    # receive_score_data()
    suspicious_words = []
    try_count        = 0

    # Try sending and receiving three times
    while try_count < 3:
        try:
            send_message( sock )
            receive_score_data( sock )

            print 'Response from server:\n{0} {1} {2}'.format(
                score,
                total_count,
                ' '.join( suspicious_words )
            )

            break
        except socket.timeout:
            # If we encounter a socket.timeout, that means two seconds passed
            # with no response from the server - try again
            print 'The server has not answered in the last two seconds.\nretrying...'
            try_count += 1

    if try_count >= 3:
        # If we tried and received more than three times, let the user know that
        # something has gone wrong
        print 'Server did not respond after three attempts.'

    sock.close()

if __name__ == "__main__":
    main( sys.argv[1:] )

sys.exit( 0 )
