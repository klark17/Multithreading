'''
The is the module defines the protocol of communication
Two simple operations are required by the file sharing system client:
Request: request a list of files the server shares
Download: send download request of the file to the server

Two simple operations are required by the file sharing system server:
List: send a list of files the server shares
File: send the file client need

Other header:
Err
@author: hao
'''

#defines the protocol header
HEAD_LIST='LST'
HEAD_REQUEST='REQ'
HEAD_DOWNLOAD='DLD'
HEAD_UPLOAD='ULD'
HEAD_FILE='FIL'
HEAD_ERROR='ERR'
HEAD_SENDCHAT='SCH'
HEAD_RECEIVECHAT='RCH'

# we prepare the message that are sent between server and client as the header + content
def prepareMsg(header, msg):
    return (header+msg).encode()

def prepareFileList(header,fList):
    '''
    function to prepare file list to msg
    '''
    msg=header
    for i in range(len(fList)):
        if (i==len(fList)-1):
            msg+=fList[i]
        else:
            msg+=fList[i]+','
    return msg.encode()

# Decode the received message, the first three letters are used as protocol header
def decodeMsg(msg):
    if (len(msg)<=3):
        return HEAD_ERROR, 'EMPTY MESSAGE'
    else:
        return msg[0:3],msg[3:len(msg)]
