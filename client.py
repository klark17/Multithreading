'''
Script for client side
@author: hao
'''
import protocol
import config
from socket import *
import os
import os.path

class client:
    
    fileList=[] # list to store the file information

    #Constructor: load client configuration from config file
    def __init__(self):
        self.serverName, self.serverPort, self.clientPort, self.localPath = config.config().readClientConfig()

    # Function to produce user menu 
    def printMenu(self):
        print("Welcome to simple file sharing system!")
        print("Please select operations from menu")
        print("--------------------------------------")
        print("1. Review the List of Available Files")
        print("2. Download File")
        print("3. Upload File")
        print("4. Quit")

    # Function to get user selection from the menu
    def getUserSelection(self):       
        ans=0
        # only accept option 1-3
        while ans>4 or ans<1:
            self.printMenu()
            try:
                ans=int(input())
            except:
                ans=0
            if (ans<=4) and (ans>=1):
                return ans
            print("Invalid Option")

    # Build connection to server
    def connect(self):
        serverName = self.serverName
        serverPort = self.serverPort
        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.connect((serverName,serverPort))
        return clientSocket

    # Get file list from server by sending the request
    def getFileList(self):
        mySocket=self.connect()
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
        mySocket=self.connect()
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

# Function to send download request to server and wait for file data
    def uploadFile(self,fileName):
        if not os.path.isfile(fileName):
            print(fileName+" is missing from the local disk!")
            return
        mySocket=self.connect()
        mySocket.send(protocol.prepareMsg(protocol.HEAD_UPLOAD, fileName))
        with open(self.localPath+"/"+fileName, 'rb') as f:
            print ('file opened')
            l = f.read(1024) # each time we only send 1024 bytes of data
            while (l):
                mySocket.send(l)
                l = f.read(1024)
            print(fileName+" has been uploaded!")
        mySocket.close()

    # Main logic of the clien, start the client application
    def start(self):
        opt=0
        while opt!=4:
            opt=self.getUserSelection()
            if opt==1:
                #if(len(self.fileList)==0): #removed this line so that we could make requests against the server and get results, if the files on the server were added/removed.
                self.getFileList()
                self.printFileList()                  
            elif opt==2:
                self.downloadFile(self.selectDownloadFile())
            elif opt==3:
                self.uploadFile(self.selectUploadFile())
            else:
                pass
                
def main():
    c=client()
    c.start()
main()
