'''
This is the file to read configuration files
Format of the server configuration file:
SERVER_PORT=SERVER_PORT_NUMBER
PATH=PATH_OF_SERVER_SHARED_DIRECTORY

Format of the client configuration file:
SERVER=SERVER_HOSTNAME/IP
SERVER_PORT=SERVER_PORT_NUMBER
CLIENT_PORT=CLIENT_PORT_NUMBER
LOCALPATH=PATH_OF_CLIENT_DOWNLOAD_DIRECTORY
NAME=NAME_OF_CLIENT

@author: hao
'''
class config:
    #define header
    server_port='SERVER_PORT'
    path="PATH"
    server="SERVER"
    client_port="CLIENT_PORT"
    localpath="LOCALPATH"
    name="NAME"
    client="CLIENT"
    serverConfig="server.config"
    clientConfig="client.config"
    
    def __init__(self):
        pass
    def readServerConfig(self):
        try:
            with open(self.serverConfig,'r') as f:
                serPort=0
                sharePath=""
                for l in f:
                    sub=l.strip().split("=")
                    if(sub[0]==self.server_port):
                        serPort=int(sub[1])
                    elif(sub[0]==self.path):
                        sharePath=sub[1]
                    else:
                        pass
                return serPort, sharePath
        except:
            print(Exception.message())
     
          
    def readClientConfig(self):
        '''
        This function read client configuration file, return five values
        @return: serverName
        @return: serverPort
        @return: clientPort
        @return: localPath
        @return: name
        @return: client
        '''
        try:
            with open(self.clientConfig,'r') as f:
                serPort=0
                serName=""
                clientPort=0
                downPath=""
                name=""
                client=""
                for l in f:
                    sub=l.strip().split("=")
                    if(sub[0]==self.server_port):
                        serPort=int(sub[1])
                    elif(sub[0]==self.server):
                        serName=sub[1]
                    elif(sub[0]==self.client_port):
                        clientPort=sub[1]   
                    elif(sub[0]==self.localpath):
                        downPath=sub[1]  
                    elif(sub[0]==self.client):
                        client=sub[1]  
                    elif(sub[0]==self.name):
                        name=sub[1]       
                    else:
                        pass  
                return serName, serPort, clientPort, downPath, name, client
        except:
            print(Exception.message())
     
# The function to test the configuration class           
def test():
    conf=config()
    client=conf.readClientConfig()
    server=conf.readServerConfig()
    print(client)
    print(server)
