'''
Script for server
@author: hao
'''

import config
import protocol
import os
import os.path
from socket import *
class server:

    # Constructor: load the server information from config file
    def __init__(self):
        self.port, self.path=config.config().readServerConfig()

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
    def receiveFile(self,serverSocket,fileName):
        with open(fileName, 'wb') as f:
            print ('file opened')
            data = serverSocket.recv(1024)
            head,msg=protocol.decodeMsg(data.decode(errors="ignore")) #ignore encoding errors.  This stream can contain either real data, or error messages, we want to decode the bytes to find errors, and if there are none, proceed.
            if head=="ERR":
                print(fileName+" ran into a problem: "+msg) #file upload failed for some reason.  Output the server error to the client.
            else:
                f.write(data)
                while data:
                    #print('receiving data...')
                    data = serverSocket.recv(1024)
                    #print('data=%s', (data))
                    f.write(data)  # write data to a file
                print(fileName+" has been uploaded!")
        serverSocket.close()

    # Main function of server, start the file sharing service
    def start(self):
        serverPort=self.port
        serverSocket=socket(AF_INET,SOCK_STREAM)
        serverSocket.bind(('',serverPort))
        serverSocket.listen(20)
        print('The server is ready to receive')
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
                self.receiveFile(connectionSocket, uploadFilename)
            else:
                connectionSocket.send(protocol.prepareMsg(protocol.HEAD_ERROR, "Invalid Message"))
            connectionSocket.close()

def main():
    s=server()
    s.start()

main()
