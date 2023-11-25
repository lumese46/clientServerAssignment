"""
  Helper functions for the server
"""


import hashlib
import os
import socket
import sys



# Get the path to the current script's directory
script_dir = os.path.dirname(os.path.abspath(sys.path[0]))
storage_dir = os.path.join(script_dir, 'server/storage')

def createTCPSocket(serverName, portNumber):
    # create TCP welcoming socket
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind((serverName, portNumber))

    return serverSocket


def savefile(fileName, data, is_protected, clientAddress):
    """
    This method saves file to the server filesystem format filename.filetype or filename.filetype-key
    if it is like this then its protected filename.filetype-key "files that have -key should not be visible to be implemented
    """
    if is_protected:
        # generate unique file name for the locked file
        uniqueFileName = fileName + str(clientAddress)
        fileNameHash = hashlib.md5(uniqueFileName.encode("utf-8")).hexdigest()
        fileName = fileName + "@" + str(fileNameHash)[0:8:1]
    else:
        print("Adding file to the openfileslist:"+fileName)
        # add open file to list of files
        openFile = open(os.path.join(sys.path[0], "openFilesList.txt"), "a")
        openFile.write(fileName + "\n")
        openFile.close()

    print("Writing File To:"+os.path.join(storage_dir, fileName))
    fileToWrite = open(os.path.join(storage_dir, fileName), "wb")
    fileToWrite.write(data)
    fileToWrite.close()
    return fileName


def checkFileExistsInServer(fileName):
    path = os.path.join(storage_dir, fileName)
    isFile = os.path.isfile(path)
    print(isFile)

    return isFile


def generateFileHash(fileName):
    """
    Generates a  hash for the file at the given filepath.
    Returns the hash as a hexadecimal string.
    """

    hashcode = hashlib.md5()
    with open(os.path.join(storage_dir, fileName), "rb") as file:
        # Read the file in chunks to avoid reading large files into memory all at once
        fileContent = file.read()
        hashcode.update(fileContent)

    return hashcode.hexdigest()


def areFilesIdentical(fileName, clientFileHash):
    """
    This method verifies the file sent by the user
    if it is the same file in storage returns True if not returns False
    """

    storedFileHash = generateFileHash(fileName)
    print("The  Stored: "+ storedFileHash)
    return storedFileHash == clientFileHash
