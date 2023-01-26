#  coding: utf-8 
import socketserver
import os


# Copyright 2023 Abram Hindle, Eddie Antonio Santos, Elena Xu
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    # how it communicates with the client
    def handle(self):
        
        try:
            # what it receives from the client
            self.data = self.request.recv(1024).strip()
            print ("Got a request of: %s\n" % self.data)

            # The idea of finding the file path through splitting the file up was found through Shane Gurusingha's 
            # implementation of their own web server (using the socket module), licensed under 
            # Creative Commons-Attribution-ShareAlike 4.0 (CC-BY-SA 4.0), found on Stack Overflow
            # Link to site where implementation was found: https://stackoverflow.com/questions/55895197/python-socket-programming-simple-web-server-trying-to-access-a-html-file-from-s
            # Link to author (in this case, the person who asked the question): https://stackoverflow.com/users/11423619/shane-gurusingha
            # Link to license: https://creativecommons.org/licenses/by-sa/4.0/
            
            methodUsed = self.data.split()[0] # e.g. GET
            filePath = self.data.split()[1]
       

            # is it a GET method?
            if methodUsed.decode().strip() != "GET":
                raise Exception

            # add the www directory at the beginning of the file path and open up the file
            modifiedFilePath = os.path.realpath('./www/' + filePath.decode()) 

            # the user has went outside of the www directory
            # /www indicates that the user is in the www directory
            if 'www/' not in modifiedFilePath and '/www' not in modifiedFilePath:
                raise Exception

            file = open(modifiedFilePath.encode()) # may raise an error
            result = file.read()
            file.close()
       
        except IsADirectoryError as e:
            # we entered a directory (either with or without /) but did not specify a file, default: use index.html
     
            if filePath.endswith(b"/"):

                # open up the appropriate file from the www directory (index.html)
                modifiedFilePath = os.path.realpath('./www/' + filePath.decode() + 'index.html') 
                file = open(modifiedFilePath.encode())
                result = file.read()
                file.close()

                # get the extension of the file (e.g. basename --> index.html)
                fileName = os.path.basename(modifiedFilePath)
                fileExtension = fileName.split('.')[1]

                self.request.send(b'HTTP/1.1 200 OK' + (f'\nContent-Type: text/{fileExtension}; charset=utf-8').encode()+ b"\r\n\r\n")
                
                # send the contents of the file (e.g. html file, css file)
                self.request.sendall(result.encode('utf-8'))

            elif not filePath.endswith(b"/"):
                
                # we need to add a / at the end
                changedFilePath = filePath.decode() + '/'
                self.request.send(b'HTTP/1.1 301 Moved Permanently\nLocation: ' + changedFilePath.encode()+ b"\r\n\r\n")

                modifiedFilePath = os.path.realpath('./www/' + filePath.decode() + '/index.html') 
                file = open(modifiedFilePath.encode())
                result = file.read()
                file.close()

                # send the contents of the file (e.g. html file, css file)
                self.request.sendall(result.encode('utf-8'))

            # in case of any other issues (e.g. file not found inside the directory) - return 404 Not Found
            else: 
                self.request.send(b'HTTP/1.1 404 Not Found\r\n\r\n')

        except Exception as e:

            methodUsed = self.data.split()[0] 
            if methodUsed.decode().strip() != "GET":
                self.request.send(b'HTTP/1.1 405 Method Not Allowed' + b'\nConnection: close' + b'\r\n\r\n')

            else:
                # For any other errors (e.g. file or directory does not exist), return 404 Not Found
                self.request.send(b'HTTP/1.1 404 Not Found\r\n\r\n')
        
        else:
            # get the extension of the file (e.g. basename --> index.html)
            fileName = os.path.basename(modifiedFilePath)
            splitFile = fileName.split('.')
            if len(splitFile) < 2 or (splitFile[-1] not in ['html', 'css']): # no file extension or it's a non-HTML or non-CSS file
                self.request.send(b'HTTP/1.1 200 OK' + b"\r\n\r\n")
            else:
                fileExtension = splitFile[-1]
                self.request.send(b'HTTP/1.1 200 OK' + (f'\nContent-Type: text/{fileExtension}; charset=utf-8').encode()+ b"\r\n\r\n")
            
            # send the contents of the file (e.g. html file, css file)
            self.request.sendall(result.encode('utf-8'))



if __name__ == "__main__":
    HOST, PORT = "localhost", 8080 
    
    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()