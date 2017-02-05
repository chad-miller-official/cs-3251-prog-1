# Programming Assignment 1: Basics of Socket Programming
### Author: Chad Miller (cmiller86@gatech.edu)
### Class: CS 3251 Section B
### Date: 4 February 2017

## Compiling

No need to compile.

## Running

The commands to run the TCP and UDP server scripts are:

* `./smsengineTCP.py <port> <suspicious words file>`
* `./smsengineUDP.py <port> <suspicious words file>`

The commands to run the TCP and UDP client scripts are:

* `./smsclientTCP.py <IP address of server> <port> <message file>`
* `./smsclientUDP.py <IP address of server> <port> <message file>`

## Known Bugs/Limitations

For some reason, I wasn't able to test any of these scripts using the network
lab machines as the server and my laptop as the client. However, I was able
to test these scripts using one network lab machine as the server and a
different network lab machine as the client.

### UDP version
* A suspicious word may not be longer than 32 characters. Luckily, there aren't
many words in the English language that exceed this limit.
* Unfortunately, messages may not be longer than 269,973 characters. The
reason for this limit is each message chunk header is represented as a 4-digit
number, meaning the maximum number of chunks is 9,999 chunks. The packet size
is defined as 32 characters, with 5 dedicated for the header and header
delimiter. Thus, 9999*(32-5) is the maximum message length.
