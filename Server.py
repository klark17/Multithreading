'''
Script for server
@author: hao
'''
import re
import time
import threading
import config
import protocol
import recipient
import os
import os.path
from datetime import datetime
from socket import *
class server:
    recipients = []
    # Constructor: load the server information from config file
    def __init__(self):
        self.port,self.path=config.config().readServerConfig()

    # Get the file names from shared directory
    def getFileList(self):
        return os.listdir(self.path)
    
    # Function to send file list to client       
    def listFile(self, serverSocket):
        serverSocket.send(protocol.prepareFileList(protocol.HEAD_LIST, self.getFileList()))

    # Function to send a file to client       
    def sendFile(self,serverSocket,fileName):
        f = open(fileName,'rb')
        l = f.read(1024) # each time we only send 1024 bytes of data
        while (l):
            serverSocket.send(l)
            l = f.read(1024)

    # Function to send a file to client       
    def receiveFile(self,serverSocket,fileName,addr):
        with open(fileName, 'wb') as f:
            increment=0
            print ('file opened')
            data = serverSocket.recv(1024)
            head,msg=protocol.decodeMsg(data.decode(errors="ignore")) #ignore encoding errors.  This stream can contain either real data, or error messages, we want to decode the bytes to find errors, and if there are none, proceed.
            if head=="ERR":
                print(fileName+" ran into a problem: "+msg) #file upload failed for some reason.  Output the server error to the client.
            else:
                f.write(data)
                while data:
                    print('receiving data ' + str(increment) + '...')
                    increment=increment+1
                    data = serverSocket.recv(1024)
                    #print('data=%s', (data))
                    f.write(data)  # write data to a file
                print("\n" + fileName + " has been uploaded from " + str(addr[0]) + " at " + str(datetime.now()) +  "!")
        serverSocket.close()
    
    #When we receive an incoming chat message from a client, capture information about the person initiating the chat (recipient) and store it in a list.  
    #This allows the server to know which clients are connected, with their name, port, and ip address
    def registerRecipient(self,message, addr):
        recip=self.convertChatToRecipient(message,addr)
        if self.recipients.count(recip)==0: #only register this recipient if the server does not know about them yet.
            self.recipients.append(self.convertChatToRecipient(message,addr))

    #convert an incoming chat message to a recipient
    def convertChatToRecipient(self,message,addr):
        name,port,chat = message.split("~")
        return recipient.recipient(name,addr[0],port)

    #Output an incoming chat message to the server console
    def printChat(self,message):
        name,port,chat = message.split("~")
        print("\n"+name + " at " + str(datetime.now()) + " said: "+chat)

    def getClientSocket(self, recipient):
        serverName = recipient.ip
        serverPort = int(recipient.port)
        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.connect((serverName,serverPort))  
        return clientSocket

    def chatRespond(self):
        while True:
            time.sleep(1) #add a slight delay here so the messaging on the server prints out in the correct order
            chat =input('Say something: ')
            match = re.search('^(@[^ ]+)', chat) #match a string that starts with @, up till the first space character.  This is our recipient.
            if not match:
                print("Your chat was not formatted correctly.  Start with @, followed by the user's name, a space, and the message you want to send")
            else:
                user = match.group() 
                recip=recipient.recipient(user.replace('@',''.replace(' ','')),'','')
                chat=re.sub('^(@[^ ]+)','',chat) #strip out the recipient from the chat
                if recip in self.recipients:
                    sock = self.getClientSocket(self.recipients[self.recipients.index(recip)]) #there is likely a more efficient way to lookup a recipient object, consider refactoring
                    sock.send(protocol.prepareMsg(protocol.HEAD_RECEIVECHAT,chat))
                    sock.close()
                    print("\nMessage Sent!")
                else:
                    print("\nI could not find a user with that name, sorry.")

    #Looks at the contents of the incoming request, and performs the desired action.  Runs on a seperate thread.
    def processRequest(self,connectionSocket,addr):
        dataRec = connectionSocket.recv(1024)
        header,msg=protocol.decodeMsg(dataRec.decode()) # get client's info, parse it to header and content
        # Main logic of the program, send different content to client according to client's requests
        if(header==protocol.HEAD_REQUEST):
            self.listFile(connectionSocket)
        elif(header==protocol.HEAD_DOWNLOAD):
            filename = self.path+"/"+msg
            if os.path.isfile(filename):
                self.sendFile(connectionSocket, filename)
            else:
                connectionSocket.send(protocol.prepareMsg(protocol.HEAD_ERROR, "File Does Not Exist"))
        elif(header==protocol.HEAD_UPLOAD):
            uploadFilename = self.path+"/"+msg
            self.receiveFile(connectionSocket, uploadFilename)
        elif(header==protocol.HEAD_SENDCHAT):
            self.registerRecipient(msg, addr)
            self.printChat(msg)
        else:
            connectionSocket.send(protocol.prepareMsg(protocol.HEAD_ERROR, "Invalid Message"))
        connectionSocket.close()
        
    # Main function of server, start the file sharing service
    def start(self):
        serverPort=self.port
        serverSocket=socket(AF_INET,SOCK_STREAM)
        serverSocket.bind(('',serverPort))
        serverSocket.listen(20)
        print('\nThe server is ready to receive.  If you wish to chat with a client, enter their name followed by the @ symbol')
        while True:    
            connectionSocket, addr = serverSocket.accept()
            dataRec = connectionSocket.recv(1024)
            header,msg=protocol.decodeMsg(dataRec.decode()) # get client's info, parse it to header and content
            # Main logic of the program, send different content to client according to client's requests
            if(header==protocol.HEAD_REQUEST):
                self.listFile(connectionSocket)
            elif(header==protocol.HEAD_DOWNLOAD):
                filename = self.path+"/"+msg
                if os.path.isfile(filename):
                    self.sendFile(connectionSocket, filename)
                else:
                    connectionSocket.send(protocol.prepareMsg(protocol.HEAD_ERROR, "File Does Not Exist"))
            elif(header==protocol.HEAD_UPLOAD):
                uploadFilename = self.path+"/"+msg
                self.receiveFile(connectionSocket, uploadFilename, addr)
            elif(header==protocol.HEAD_SENDCHAT):
                self.registerRecipient(msg, addr)
                self.printChat(msg)
            else:
                connectionSocket.send(protocol.prepareMsg(protocol.HEAD_ERROR, "Invalid Message"))
            connectionSocket.close()
            connectionSocket.settimeout(60)
            threading.Thread(target = self.processRequest,args = (connectionSocket,addr)).start()

def main():
    s=server()
    thread1 = threading.Thread(target=s.start)
    thread2 = threading.Thread(target=s.chatRespond)
    thread1.start()
    thread2.start()

main()
