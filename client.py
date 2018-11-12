'''
Script for client side
@author: hao
'''
import re
import time
from clientChat import clientChat
from datetime import datetime
import threading
import protocol
import config
from socket import *
import os
import os.path

class client:
    
    fileList=[] # list to store the file information
    chat=clientChat() #an object that manages client chat functionality
    #Constructor: load client configuration from config file
    def __init__(self):
        self.serverName, self.serverPort, self.clientPort, self.localPath, self.name, self.clientName = config.config().readClientConfig()

    # Function to produce user menu 
    def printMenu(self):
        
        print("Welcome to simple file sharing system " + self.name + "!")
        print("Please select operations from menu")
        print("--------------------------------------")
        print("1. Review the List of Available Files")
        print("2. Download File")
        print("3. Upload File")
        print("4. Send a message to the server")
        print("5. Quit")

    # Function to get user selection from the menu
    def getUserSelection(self):       
        ans=0
        # only accept option 1-5
        while ans>5 or ans<1:
            self.printMenu()
            try:
                ans=int(input())
            except:
                ans=0
            if (ans<=5) and (ans>=1):
                return ans
            print("Invalid Option")

    # Build connection to server
    def connect(self, serverName, serverPort):
        try:
            clientSocket = socket(AF_INET, SOCK_STREAM)
            clientSocket.connect((serverName,int(serverPort)))
            return clientSocket
        except RuntimeError as e:
            print("\nThere was a problem connecting to the server, try again later: " + e + "\n")
            return

    # Get file list from server by sending the request
    def getFileList(self):
        mySocket=self.connect(self.serverName,self.serverPort)
        if mySocket is None:
            return
        mySocket.send(protocol.prepareMsg(protocol.HEAD_REQUEST," "))
        header, msg=protocol.decodeMsg(mySocket.recv(1024).decode())
        mySocket.close()
        if(header==protocol.HEAD_LIST): 
            files=msg.split(",")
            self.fileList=[]
            for f in files:
                self.fileList.append(f)
        else:
            print ("Error: cannnot get file list, or server has no files.")

    # function to print files in the list with the file number
    def printFileList(self):
        count=0
        for f in self.fileList:
            count+=1
            print('{:<3d}{}'.format(count,f))

    def getLocalFileList(self):
        self.fileList=os.listdir(self.localPath)

    # Function to select the file from file list by file number,
    # return the file name user selected
    def selectDownloadFile(self):
        self.getFileList()
        ans=-1
        while ans<0 or ans>len(self.fileList)+1:
            self.printFileList()
            print("Please select the file you want to download from the list (enter the number of files):")
            try:
                ans=int(input())
            except:
                ans=-1
            if (ans>0) and (ans<len(self.fileList)+1):
                return self.fileList[ans-1]
            print("Invalid number")

# Function to select the file from file list by file number,
    # return the file name user selected
    def selectUploadFile(self):
        self.getLocalFileList()
        ans=-1
        while ans<0 or ans>len(self.fileList)+1:
            self.printFileList()
            print("Please select the file you want to upload from the list (enter the number of files):")
            try:
                ans=int(input())
            except:
                ans=-1
            if (ans>0) and (ans<len(self.fileList)+1):
                return self.fileList[ans-1]
            print("Invalid number")

    # Function to send download request to server and wait for file data
    def downloadFile(self,fileName):
        mySocket=self.connect(self.serverName,self.serverPort)
        if mySocket is None:
            return
        mySocket.send(protocol.prepareMsg(protocol.HEAD_DOWNLOAD, fileName))
        with open(self.localPath+"/"+fileName, 'wb') as f:
            print ('file opened')
            data = mySocket.recv(1024)
            head,msg=protocol.decodeMsg(data.decode(errors="ignore")) #ignore encoding errors.  This stream can contain either real data, or error messages, we want to decode the bytes to find errors, and if there are none, proceed.
            if head=="ERR":
                print(fileName+" ran into a problem: "+msg) #file download failed for some reason.  Output the server error to the client.
            else:
                f.write(data)
                while data:
                    #print('receiving data...')
                    data = mySocket.recv(1024)
                    #print('data=%s', (data))
                    f.write(data)  # write data to a file
                print(fileName+" has been downloaded!")
        mySocket.close()

    # A Function that sends an upload request to the file server, and uploads the specified filename
    def uploadFile(self,fileName):
        #increment=0
        if not os.path.isfile(self.localPath+"/"+fileName):
            print(fileName+" is missing from the local disk!")
            return
        mySocket=self.connect(self.serverName,self.serverPort)
        if mySocket is None:
            return
        mySocket.send(protocol.prepareMsg(protocol.HEAD_UPLOAD, fileName))
        time.sleep(0.5) #add a slight delay here, we found in testing that if we send this request and the first file request at the same time, we can't control which arrives first, which means the server can't decide what to do with the incoming file.  This helps mitigate that issue, but this is likely not an ideal solution
        with open(self.localPath+"/"+fileName, 'rb') as f:
            print(fileName+" reading initial data")
            l = f.read(1024) # each time we only send 1024 bytes of data
            while (l):
                mySocket.send(l)
                time.sleep(0.1) #add an artifical delay so we can more easily watch multiple downloads/uploads from the server
                #print(fileName+" sending data " + str(increment))
                #increment=increment+1
                l = f.read(1024)
            print(fileName+" has been uploaded!")
        mySocket.close()

   

    # Main logic of the client, start the client application
    def start(self):
        opt=0
        thread1 = threading.Thread(target=self.chat.chatListen) #start the chat service on a seperate thread
        thread1.start()
        while opt!=5:
            opt=self.getUserSelection()
            if opt==1: #list the files available on both the local disk and remote server
                #if(len(self.fileList)==0): #removed this line so that we could make requests against the server and get results, if the files on the server were added/removed.
                print('\nThese are the files available on the remote server:')
                self.getFileList()
                self.printFileList()    
                print('\nThese are the files available on your local disk:')
                self.getLocalFileList()
                self.printFileList()                  
            elif opt==2:
                self.downloadFile(self.selectDownloadFile())
            elif opt==3:
                self.uploadFile(self.selectUploadFile())
            elif opt==4:
                self.chat.sendChat()
            else:
                sock=self.connect(self.clientName,self.clientPort)
                #send a message to that port to wake it up, so that the while loop can terminate
                #this is necessary because we cannot terminate our client unless the chat thread is allowed to gracefully terminate
                sock.send(protocol.prepareMsg(protocol.HEAD_TERMINATECHAT, 'Exiting')) 
                sock.close()
                
def main():
    c=client()
    c.start()
main()
