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
import select

#slitly modifided code for spliting messages from server
def parsemsg(s):
    #print(s)
    """Breaks a message from an IRC server into its sender, prefix, command, and arguments.
    """
    sender = ''
    prefixpar = ''
    trailing = []
    commandpar = ''
    if not s:
        print("no response from server")
    else:
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
username = 'conbot'

#function variables
botname = 'conbot1'
isstatus = False
isattack = False
ismove = False
isshutdown = False
isquit = False
iscommand = True
numsuccess = 0
numunsuccess = 0

#runtime boolean
shutoff = False
isconnected = False
issocket = False
isname = False
issent = False
tnow = time.time()



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

#this must be in a loop, if disconnected try again in 5 sec
while not isquit:
    #loop until connected to irc server
    while not issocket:
        isconnected = False
        isname = False
        issent = False
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
        print("Connected to Socket")
        try:
            """ircsocket.send("NICK {}\r\n".format(botname).encode("utf-8"))
            ircsocket.send("USER {} 0 * :{}\r\n".format(username, username).encode("utf-8"))
            isconnected = True
            """
            while not isname:
                ircsocket.send("NICK {}\r\n".format(botname).encode("utf-8"))
                if not issent:
                    ircsocket.send("USER {} 0 * :{}\r\n".format(username, username).encode("utf-8"))
                    issent = True
                if(not issocket):
                    break
                while not isname:
                    ircinput = ircsocket.recv(1024).decode("utf-8")
                    #print(ircinput)
                    if isping(ircinput, ircsocket):
                        continue
                    user, prefix, command, args = parsemsg(ircinput)
                    if "NOTICE" in command:
                        if "Welcome" in args[1]:
                            print("Connected to irc")
                            isname = True
                            isconnected = True
                            break
                    elif command == "ERROR":
                        print("there was an error:", args)
                        issocket = False
                        ircsocket.close()
                        ircsocket = socket.socket()
                        break
                    elif "433" in command:
                        print("botname failed:", botname)
                        botname = 'bot' + str(random.randint(0, 1000))
                        break
                if(not issocket):
                    break
                else:
                    print("waiting to join channel")
                    time.sleep(5)
                    ircsocket.send("JOIN {}\r\n".format(channel).encode("utf-8"))
                    print("JOIN {}\r\n".format(channel))
                    time.sleep(2)
                    ircsocket.send("PRIVMSG {} :{}\r\n".format(channel, secret).encode("utf-8"))
        except OSError:
            print("Retrying to connect to socket")
            issocket = False
            ircsocket.close()
            ircsocket = socket.socket()
    if not issocket:
        continue

    #loop to send or recive to/from socket
    try:
        if(time.time() > tnow and iscommand):
            if isstatus:
                isstatus = False
                print("found: {} bots".format(numsuccess))
            elif isattack:
                isattack = False
                print("{} successful, {} unsuccessful".format(numsuccess, numunsuccess))
            elif ismove:
                ismove = False
                print("found: {} bots".format(numsuccess))
            elif isshutdown:
                print("{} bots has shutdown".format(numsuccess))
                isshutdown = False
            iscommand = False
            print("input command:")
        r, w, x = select.select([ircsocket, sys.stdin], [], [], 1)
        if ircsocket in r:
            ircinput = ircsocket.recv(1024).decode("utf-8")
            if not isping(ircinput, ircsocket):
                user, prefix, command, args = parsemsg(ircinput)
                if isstatus:
                    if "I am a bot" in args[1]:
                        print(user)
                        numsuccess += 1
                elif isattack:
                    if "attack sucessful" in args[1]:
                        print(user, " attack successful")
                        numsuccess += 1
                    elif "attack failed" in args[1]:
                        print(user, " attack failed")
                        numunsuccess += 1
                elif ismove:
                    if "moving to new server" in args[1]:
                        print(user, "have moved")
                        numsuccess += 1
                elif isshutdown:
                    if "shutting down" in args[1]:
                        print(user, "have shutdown")
                        numsuccess += 1
            #read the stuff, and work it out
        if sys.stdin in r and time.time() > tnow:
            userinput = sys.stdin.readline()
            print("user input is:", userinput)
            #set command flag
            if "status" in userinput:
                isstatus = True
                iscommand = True
            elif "attack" in userinput:
                isattack = True
                iscommand = True
            elif "move" in userinput:
                ismove = True
                iscommand = True
            elif "shutdown" in userinput:
                iscommand = True
                isshutdown = True
            elif "quit" in userinput:
                iscommand = True
                isquit = True
            ircsocket.send("PRIVMSG {} :{}\r\n".format(channel, userinput).encode("utf-8"))
            if iscommand:
                tnow = time.time() + 5
                numsuccess = 0
                numunsuccess = 0

    except socket.timeout:
        continue
    except OSError:
        print("Connection to server has fail: reconnecting")
        issocket = False
        ircsocket.close()
        ircsocket = socket.socket()


