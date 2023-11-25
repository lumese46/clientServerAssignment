import sys # for command line arguments 
import os 
import hashlib
import socket
import pickle

#print (sys.argv[0])

# generate by byte filesize
def getfilesize(filename):
    file_stats = os.stat(filename)
    filesize = file_stats.st_size
    return filesize

# generate hash
def genfilehash(filename):
    hashcode = hashlib.md5()
    with open(filename,'rb') as open_file:
        fileContent = open_file.read()
        hashcode.update(fileContent)
    filehash = hashcode.hexdigest()
    return filehash

# check if the program took valid commandline arguments
def checkcommandLineArgs():
    # number of commandline Args
    commandLineArgs =  len(sys.argv)    
    if ( commandLineArgs == 4):
        return True   
    else:
        return False
    
    
    
# get upload info from user and return message header
def downloadinfo():
    # get file name from user
    filename = input("Enter the name of the file(E.g file.txt):\n")
    # get file protection size
    protected = input("The Protection status of the File(True or False):\n")
    # get the key of the file
    key =  input("Enter the key of the file (only if the file is protected if not  enter  ):\n")
    # message header
    return f"{requests},{filename},{protected},{key}"
#download process
def DownloadProcess(msgHeader):
    
    
    print("\nSending connection Request to the Server...")
    # receive server connection response 
    msg = clientSocket.recv(1024)   
    d = pickle.loads(msg)
    print(d)  
    
    
    print("\nSending Download Request to the Server...\n")
    # send upload request 
    msg = msgHeader
    msg = pickle.dumps(msg)
    clientSocket.send(msg)  
    
    print("\nReceiving Download header/Response from the Server...\n")
    #receive server message header  print it
    # message have the format --> filesize to be used below when we receive and fileveryfyhash toverify if we downloaded right file
    msg = clientSocket.recv(1024)   
    d = pickle.loads(msg)
    requestHeader = d.split(",") 
    
    
    # prepare for download
    if  len(requestHeader) == 2 and requestHeader[0] != "Access Denied" :
        # receive the file/download file
        data = clientSocket.recv(int(requestHeader[0]))# file byte size will be received from server message header 160892
        file = open("download.png", "wb")
        file.write(data)    
        file.close() 
        
        # receive server response  message
        msg= clientSocket.recv(1024)   
        d = pickle.loads(msg)
        print(d) 
    else:
        print(requestHeader[0])
    
    
    
    


# get upload info from user and return message header
def uploadinfo():
    # get file name from user
    filename = input("Enter the name of the file(E.g file.txt):\n")
    # get file byte size
    filesize = getfilesize(filename)
    # get file protection size
    protected = input("The Protection of the File(True or False):\n")
    # generate md5checksum hash for file verification
    fileverifyhash = genfilehash(filename) 
    # message header
    return f"{requests},{filename},{filesize},{protected},{fileverifyhash}"

#upload process
def UploadProcess(msgHeader):
    print("\nSending connection Request to the Server...")
    # receive server connection response 
    msg = clientSocket.recv(1024)   
    d = pickle.loads(msg)
    print(d)  
    
    print("\nSending Upload Request to the Server...\n")
    
    # send upload request 
    msg = msgHeader
    msg = pickle.dumps(msg)
    clientSocket.send(msg)
    
    # sending the file to the server
    # open the file 
    # split the request header into attributes
    requestHeader = msgHeader.split(",")    
    file = open(requestHeader[1],"rb")
    # reading the image
    data = file.read()
    # sending the file
    clientSocket.sendall(data)    
    
    
    #receive server response and print it
    print("Server Response in the form {Status , filename , key(if file is protected )}")
    msg= clientSocket.recv(1024)   
    d = pickle.loads(msg) 
    print(d)  
    
def ListallProcess(requests):
    
    print("\nSending connection Request to the Server...")
    # receive server connection response 
    msg = clientSocket.recv(1024)   
    d = pickle.loads(msg)
    print(d)    
    
    print("\nSending Upload Request to the Server...\n")
    # send upload request 
    msg = requests
    msg = pickle.dumps(msg)
    clientSocket.send(msg)    
    
    #receive server response and print it
    print("Server Response in the form {Status , filename , key(if file is protected )}")
    msg= clientSocket.recv(1024)   
    d = pickle.loads(msg) 
    print(d)     
    
    
    
    
    

##################Program######################
# only runs if the correct commandline arguments are given
if checkcommandLineArgs():
    serverName = sys.argv[1]
    serverPort = int(sys.argv[2]) 
    requests = sys.argv[3]
    #requests = "UPLOAD"
    
    # create client Socket
    clientSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    # Connect with the server 
    clientSocket.connect((serverName,serverPort))
    
    if requests == "UPLOAD":
        # get more info from the user and return message header
        msgHeader = uploadinfo()
        # start upload process
        UploadProcess(msgHeader)
    elif requests == "DOWNLOAD":
        # get more info from the user and return message header
        msgHeader = downloadinfo() 
        # start upload process
        DownloadProcess(msgHeader) 
    elif requests == "LISTALL":
        ListallProcess(requests)
    
    
    
    


###############################################