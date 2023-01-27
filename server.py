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

'''
External sources used:

(Used to give me an idea on how to approach opening the files, and sending the content back as well extra headers)

1. Shane Gurusingha's implementation of their own web server (using the socket module), licensed under 
Creative Commons-Attribution-ShareAlike 4.0 (CC-BY-SA 4.0), found on Stack Overflow (https://stackoverflow.com/)

Title of question: Python Socket Programming Simple Web Server, Trying to access a html file from server
Year: 2019
Link to site where implementation was found: https://stackoverflow.com/questions/55895197/python-socket-programming-simple-web-server-trying-to-access-a-html-file-from-s
Link to author (in this case, the person who asked the question): https://stackoverflow.com/users/11423619/shane-gurusingha
Link to license: https://creativecommons.org/licenses/by-sa/4.0/

2. Emalsha Rasad's implemention of their own web server (using the socket module), found on their blog (https://emalsha.wordpress.com/)

Titles: How create HTTP-Server using python Socket – Part I and How create HTTP-Server using python Socket – Part II
Year: 2016
Link to part 1: https://emalsha.wordpress.com/2016/11/22/how-create-http-server-using-python-socket/
Link to part 2: https://emalsha.wordpress.com/2016/11/24/how-create-http-server-using-python-socket-part-ii/
'''

class InvalidMethodError(Exception):
    pass

class OutsideDirectoryError(Exception):
    pass


class MyWebServer(socketserver.BaseRequestHandler):
    
    # how it communicates with the client
    def handle(self):
        
        try:
            # what it receives from the client
            self.data = self.request.recv(1024).strip()
            print ("Got a request of: %s\n" % self.data)
            
            methodUsed = self.data.split()[0] # e.g. GET
            filePath = self.data.split()[1]
            
            # is it a GET method?
            if methodUsed.decode().strip() != "GET":
                raise InvalidMethodError

            # add the www directory at the beginning of the file path and open up the file
            modifiedFilePath = os.path.realpath('./www' + filePath.decode()) 

            # the user has went outside of the www directory
            # /www indicates that the user is in the www directory
            if 'www/' not in modifiedFilePath and '/www' not in modifiedFilePath:
                raise OutsideDirectoryError

            file = open(modifiedFilePath.encode()) # may raise an error
            result = file.read()
            file.close()
       
        except IsADirectoryError:
            # we entered a directory (either with or without /) but did not specify a file, default: use index.html
            currentPath = './www/' + filePath.decode() 

            if filePath.endswith(b"/") and os.path.exists(currentPath + 'index.html'):

                modifiedFilePath = os.path.realpath(currentPath + 'index.html') 
                
                # open up index.html
                file = open(modifiedFilePath.encode())
                result = file.read()
                file.close()

                # get the extension of the file (e.g. basename --> index.html)
                fileName = os.path.basename(modifiedFilePath)
                fileExtension = fileName.split('.')[-1]

                self.request.send(b'HTTP/1.1 200 OK' + (f'\nContent-Type: text/{fileExtension}; charset=utf-8').encode()+ b"\r\n\r\n")
                
                # send the contents of the file (e.g. html file, css file)
                self.request.sendall(result.encode())

            elif not filePath.endswith(b"/"):
                
                # we need to add a / at the end
                changedFilePath = filePath.decode() + '/'
                self.request.send(b'HTTP/1.1 301 Moved Permanently\nLocation: ' + changedFilePath.encode() + b"\r\n\r\n")

            # in case of any other issues (e.g. index.html does not exist)
            else: 
                self.request.send(b'HTTP/1.1 404 Not Found' + b'\r\n\r\n')

        except InvalidMethodError:
            self.request.send(b'HTTP/1.1 405 Method Not Allowed' + b'\r\n\r\n')

        except OutsideDirectoryError:
            # For any files outside of the www directory, return 404 not found
            self.request.send(b'HTTP/1.1 404 Not Found' + b'\r\n\r\n')

        except Exception: 
            # In case of any other errors, return 404 not found
            self.request.send(b'HTTP/1.1 404 Not Found' + b'\r\n\r\n')

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
            self.request.sendall(result.encode())



if __name__ == "__main__":
    HOST, PORT = "localhost", 8080 
    
    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
