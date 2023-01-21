#  coding: utf-8 
import socketserver
import os


# Copyright 2013 Abram Hindle, Eddie Antonio Santos, Elena Xu
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
           

            # finding a way to get the file path (can just split it)
            # https://stackoverflow.com/questions/55895197/python-socket-programming-simple-web-server-trying-to-access-a-html-file-from-s
            methodUsed = self.data.split()[0]
            filePath = self.data.split()[1]
            print(self.data)
            print("FILEPATH", filePath)

            modifiedFilePath = os.path.realpath('./www/' + filePath[1:].decode())
            file = open(modifiedFilePath.encode())
            result = file.read()
            file.close()
         


            # did the server succeed in processing the request - send the status code
            if methodUsed.decode().strip() != "GET":
                self.request.send(b'HTTP/1.1 405 Method Not Allowed\r\n\r\n')
            else:
                self.request.send(b'HTTP/1.1 200 OK\r\n\r\n')
       
            self.request.sendall(result.encode('utf-8'))

     

            #  self.request.sendall(bytearray("OK",'utf-8'))
        except IsADirectoryError as e:
            #print(e)
            path1 = './www'
            path2 = os.path.realpath('./www/' + filePath[1:].decode())
            print("PATH2", "this:"+filePath[1:].decode(), "2:", path2)
     

            if filePath.decode().endswith("/") and 'www' in path2:
                changedFilePath = f'http://{HOST}:{PORT}' + filePath.decode() + 'index.html' 
                self.request.send(b'HTTP/1.1 301 Moved Permanently\nLocation: ' + changedFilePath.encode()+ b"\n\n")
            elif 'www' in path2:
                changedFilePath = f'http://{HOST}:{PORT}' + filePath.decode() + '/index.html' 
                self.request.send(b'HTTP/1.1 301 Moved Permanently\nLocation: ' + changedFilePath.encode()+ b"\n\n")
            if 'www' not in path2:
                #raise Exception
                self.request.send(b'HTTP/1.1 404 Not Found\r\n\r\n')
        except Exception as e:
            print(e)
            self.request.send(b'HTTP/1.1 404 Not Found\r\n\r\n')


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
