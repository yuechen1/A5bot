# pylint: disable=C0103
# pylint: disable=C1001
# pylint: disable=R0903
# pylint: disable=C0301
#run irc server using!!!! sudo service inspircd start
import socket
import sys
import time


#slitly modifided code for spliting messages from server
def parsemsg(s):
    """Breaks a message from an IRC server into its sender, prefix, command, and arguments.
    """
    sender = ''
    prefix = ''
    trailing = []
    command = ''
    if not s:
        print 'no response from server'
    if s[0] == ':':
        prefix, s = s[1:].split(' ', 1)
        sender, prefix = prefix.split("!", 1)
    if s.find(' :') != -1:
        s, trailing = s.split(' :', 1)
        args = s.split()
        args.append(trailing)
    else:
        args = s.split()
    command = args.pop(0)
    return sender, prefix, command, args

def isping(s, sock):
    """Breakdown the message to see if it is a ping message"""
    ping, rest = s.split(' ', 1)
    if ping == 'PING':
        pong = 'PONG' + rest
        sock.send(pong.encode("utf-8"))
        return True
    else:
        return False

#needed variables
hostname = ''
port = 0
channel = ''
secret = ''

poweruser = []
attackhost = ''
attackport = ''

shutoff = False
isconnected = False



if len(sys.argv) != 5:
    print 'invalid input'

#get information from commandline
try:
    hostname = sys.argv[1]
    (int)(port=sys.argv[2])
    channel = sys.argv[3]
    secret = sys.argv[4]
except ValueError:
    print('invalid input: ', sys.argv[2])

#connect to server
ircsocket = socket.socket()
socket.setdefaulttimeout(1000)

#this must be in a loop, if disconnected try again in 5 sec
while not shutoff:
    #loop until connected to irc server
    while ircsocket == -1:
        try:
            ircsocket.connect((socket.gethostbyname(hostname), port))
        except socket.timeout:
            ircsocket = -1
            time.sleep(5)
        except OSError:
            print 'cannot connect to ircserver'
            ircsocket = -1
            time.sleep(5)
    #loop until a user use the secret password
    ircinput = ircsocket.recv(1024).decode("utf-8")
    if not isping(ircinput):
        
    #wait for command from that user
    #if a command is issued carry it out



