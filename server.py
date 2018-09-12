"""
Lab 2 - HTTP Server
NAME: Silke Knossen
STUDENT ID: 11025948
DESCRIPTION:
"""

import socket
import socketserver
import pprint
import time
import cgi
import os
import sys
import mimetypes
# import magic
import subprocess

def serve(port, public_html, cgibin):
    """
    The entry point of the HTTP server.
    port: The port to listen on.
    public_html: The directory where all static files are stored.
    cgibin: The directory where all CGI scripts are stored.
    """
    host = "127.0.0.1"
    serverSocket = socket.socket()
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSocket.bind((host, port))
    serverSocket.listen(5)

    while True:
        connection, address = serverSocket.accept()
        print("connection from", connection, address)
        message = connection.recv(10240000)
        message = bytes.decode(message, "utf-8")
        print(message)

        requestMethod = message.split(' ')[0]

        if requestMethod == 'GET':
            requestFile = message.split(' ')[1]
            requestFile = requestFile.split('?')[0]
            print('REQUESTED FILE', requestFile)

            # cgibin.enable()
            if requestFile[:8] == '/cgi-bin':
                response = handle_cgi(connection, requestFile)

            else:
                response = handle_request(connection, requestFile)

            print('Send response to client')
            connection.send(response)


        else:
            content = b'<html><body<h>Error 501: \
                        Not Implemented</h></body></html>'
            responseHeader = get_headers(501, None, content)
            responseHeader = responseHeader.encode()
            response = responseHeader + content

            print('Send response to client')
            connection.send(response)

        print('Closing connection with the client')
        connection.close()


def get_headers(code, responseFile, content):
    """
    """
    if code == 200:
        header = 'HTTP/1.1 200 OK\r\n'
    if code == 404:
        header = 'HTTP/1.1 404 Not Found\r\n'
    if code == 501:
        header = 'HTTP/1.1 501 Not Implemented\r\n'

    date = time.strftime('%a, %d %b %Y %H:%M:%S GMT')
    print(date)
    print('RESPONSE FILE ', responseFile)
    print('CONTENT ', content)
    length = str(len(content))

    if responseFile != None:
        content_type = mimetypes.guess_type(responseFile)[0]
        # # with open(responseFile, 'rb') as fileHandle:
        # #     content = fileHandle.read()
        # #     print('HALLOOOO4')
        # #     print(content)
        # length = os.stat(responseFile).st_size
        #     # fileHandle.close()
        # print('HALLOOOOO5')
    else:
        content_type = 'text/html'

    header += 'Content-Type: ' + content_type + '\r\n'
    header += 'Content-Length: ' + length + '\r\n'
    header += 'Connection: close\r\n'
    header += 'Date: ' + date + '\r\n'
    header += 'Server: Cute-HTTP-Server-Which-Can-Do-Anything\r\n\r\n'

    print('HALLO HEADER', header)
    return header

def handle_request(connection, requestFile):
    if requestFile == '/':
        requestFile = '/index.html'

    requestFile = public_html + requestFile
    print("requested file is at", requestFile)

    try:
        with open(requestFile, 'rb') as fileHandle:
            content = fileHandle.read()
            fileHandle.close()

        responseHeader = get_headers(200, requestFile, content)

    except Exception as e:
        content = b'<html><body><h>Error 404: \
                    File not found</h></body></html>'
        responseHeader = get_headers(404, None, content)

    responseHeader = responseHeader.encode()
    response = responseHeader + content
    return response

def handle_cgi(connection, requestScript):
    script = requestScript.split('/')[2]
    print('SCRIPT', script)
    script_path = cgibin + '/' + script

    try:
        output = subprocess.call(script)
        header = 'HTTP/1.1 200 OK\r\n'
        print(output)
        print('DID IT')

    except:
        header = 'HTTP/1.1 404 Not Found\r\n'

    response = header.encode()
    return response


# This the entry point of the script.
# Do not change this part.
if __name__ == '__main__':
    import os
    import sys
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--port', help='port to bind to', default=8080, type=int)
    p.add_argument('--public_html', help='home directory',
                   default='./public_html')
    p.add_argument('--cgibin', help='cgi-bin directory', default='./cgi-bin')
    args = p.parse_args(sys.argv[1:])
    public_html = os.path.abspath(args.public_html)
    cgibin = os.path.abspath(args.cgibin)
    serve(args.port, public_html, cgibin)
