from enum import Enum
import os
import hashlib
import socket
import pickle
import sys

from serverUtils import (
    areFilesIdentical,
    checkFileExistsInServer,
    createTCPSocket,
    generateFileHash,
    savefile,
)


class RequestOption(Enum):
    UPLOAD = 1
    DOWNLOAD = 2
    LISTALL = 3

# Get the path to the current script's directory
script_dir = os.path.dirname(os.path.abspath(sys.path[0]))
storage_dir = os.path.join(script_dir, 'server/storage')

class Server:
    def __init__(self, hostName, portNumber) -> None:
        # create socket and listen to incoming requests.
        self.serverSocket = createTCPSocket(hostName, portNumber)
        self.connectionSocket=None
        self.clientAddress =None
        self.serverSocket.listen(5)
        print("The Server Is Ready...")

    def startServer(self):
        # loos forever always on host
        while True:
            # accepts connection and create new socket for the client.
            self.connectionSocket, self.clientAddress = self.serverSocket.accept()

            # the server accepts connection
            sentence = f"Connection established with {self.clientAddress}, Server is ready to receive requests."
            self.connectionSocket.send(pickle.dumps(sentence))

            # receive client requests
            request= self.connectionSocket.recv(1024)
            request = pickle.loads(request)
            
            requestHeader = request.split(",")
            headerLen = len(requestHeader)
            print("Request Header: "+ str(requestHeader))
            if requestHeader[0] == RequestOption.UPLOAD.name and headerLen == 5:
                uploadResponse = self.processUpload(
                    fileName=requestHeader[1],
                    fileSize=int(requestHeader[2]),
                    protected=requestHeader[3],
                    fileHash=requestHeader[4]
                )
                print(uploadResponse)
                # send the response
                msg = pickle.dumps(uploadResponse)
                self.connectionSocket.send(msg)

            elif requestHeader[0] == RequestOption.DOWNLOAD.name and headerLen == 4:
                downloadResponse = self.processDownload(
                    fileName=requestHeader[1],
                    protected=requestHeader[2],
                    key=requestHeader[3],
     
                )
                # send the response
                msg = pickle.dumps(downloadResponse)
                self.connectionSocket.send(msg)

            elif requestHeader[0] == RequestOption.LISTALL.name and headerLen == 1:
                # to take no input -->
                listResponse = self.processListAllFiles()
                msg = pickle.dumps(listResponse)
                self.connectionSocket.send(msg)

            else:
                # for an Invalid response
                msg = "Invalid Request"
                msg = pickle.dumps(msg)
                self.connectionSocket.send(msg)
            
            # close the clients
            self.connectionSocket.close()

    def sendDownloadHeader(self,fileName):
        # generate filesize
        file_stats = os.stat(os.path.join(storage_dir, fileName))
        print(file_stats)
        filesize = file_stats.st_size

        # generate hash
        serverFileHash = generateFileHash(fileName)
        print(serverFileHash)

        # send the header to the client
        responseMsg = pickle.dumps(f"{filesize},{serverFileHash}")
        print(responseMsg)
        self.connectionSocket.send(responseMsg)

    def sendToClient(self,fileName):
        """
        Sends file to the client
        """
        print("Sending Client: "+fileName)
        file = open(os.path.join(storage_dir, fileName), "rb")
        data = file.read()
        
        # send
        self.connectionSocket.sendall(data)

    def processUpload(
        self, fileName, fileSize, protected, fileHash
    ):
        print("Uploading: " + fileName)
        # receive data stream from client and stops receiving when all dytes are recevied.
        responseMsg = ""
        fileData = self.connectionSocket.recv(fileSize)
   
        storedFileName = savefile(fileName,fileData, protected == "True", self.clientAddress)
        
        if areFilesIdentical(storedFileName, fileHash):
            if protected == "True":
                parts = storedFileName.split("@")
                cleanName = parts[0]
                fileKey = parts[1]
                responseMsg = f"File uploaded,{cleanName},{fileKey}"
            else:
                responseMsg = f"File uploaded,{storedFileName}"
        else:
            if protected == "True":
                storedFileName = storedFileName.split("@")[0]
            responseMsg = f"File is corrupted,{storedFileName}"

        return responseMsg

    def processDownload(self, fileName, protected, key):
        responseMsg = ""
        print("Dpwnlaoding")
        if protected == "True":  # change to convention
            fileNameInServer = fileName + "@" + key
            fileExist = checkFileExistsInServer(fileNameInServer)
            if fileExist:
                self.sendDownloadHeader(fileNameInServer)
                self.sendToClient(fileNameInServer)
                responseMsg = "File Sent"
            else:  # to access protected filename + key must both be valid
                responseMsg = "Access Denied, Unauthorized access"

        else:  # open file
            fileExist = checkFileExistsInServer(fileName)
            if fileExist:
                self.sendDownloadHeader(fileName)
                self.sendToClient(fileName)
                responseMsg = "File sent"
            else:
                responseMsg = "File does not exist"

        return responseMsg

    def processListAllFiles(self):
        names = open(os.path.join(sys.path[0], "openFilesList.txt"), "r")
        return names.read()


if __name__ == "__main__":
    fileServer = Server("localhost", 9024)
    fileServer.startServer()
   
