'''
Script for client side
@author: nate suver and kam larkins
'''
import re
from datetime import datetime
import threading
import protocol
import config
from socket import *
import os
import os.path

class clientChat:
    chatSocket=socket(AF_INET,SOCK_STREAM)
    #Constructor: load client configuration from config file
    def __init__(self):
        self.serverName, self.serverPort, self.clientPort, self.localPath, self.name, self.clientName = config.config().readClientConfig()

    # Build connection to server
    def connect(self, serverName, serverPort):
        try:
            clientSocket = socket(AF_INET, SOCK_STREAM)
            clientSocket.connect((serverName,serverPort))
            return clientSocket
        except:
            print("\nThere was a problem connecting to the server, try again later\n")
            return

    #Given chat data from our user, construct a tilde delimited string that we can send to the server.  Each chat must contain the name of the recipient, the port any responses should come to, and the chat itself
    def constructChat(self,chat):
        return self.name+"~"+self.clientPort+"~"+chat.replace("~","") #scrub special characters from the input

    #Accept keyboard input and send a chat to a connected server
    def sendChat(self):
        chat=input('\nWhat would you like to say?  ')
        mySocket=self.connect(self.serverName,self.serverPort)
        if mySocket is None:
            return
        mySocket.send(protocol.prepareMsg(protocol.HEAD_SENDCHAT, self.constructChat(chat)))
        print("\nMessage Sent!")

    #listen for incoming chats from the server
    def chatListen(self):
        self.chatSocket.bind((self.clientName,int(self.clientPort)))
        self.chatSocket.listen(20)
        while True:
            connectionSocket, addr = self.chatSocket.accept()
            dataRec = connectionSocket.recv(1024)
            header,chat=protocol.decodeMsg(dataRec.decode())
            if(header==protocol.HEAD_RECEIVECHAT):
                print("\nServer responded at " + str(datetime.now()) + " and said: "+chat)
            if(header==protocol.HEAD_TERMINATECHAT): #client requests that the chat thread should terminate
                break