from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import os.path
import json
import socket

ROOT_STATIC_FOLDER = None
SOCKET_HOST = None
SOCKET_PORT = None

class HttpHandler(BaseHTTPRequestHandler):

    def __parse_url(self):
        return urllib.parse.urlparse(self.path)

    def __get_extension(self, filename):
        return os.path.splitext(filename)[1]

    def do_GET(self):
        #print("GET")
        url = self.__parse_url()
        if url.path == "/":
            self.__send_static_file('index.html', ("Content-type", 'text/html'))
        elif self.__get_extension(url.path) == '.css':
            self.__send_static_file(url.path[1:], ("Content-type", "text/css"))
        elif self.__get_extension(url.path) == '.png':
            self.__send_static_file(url.path[1:], ("Content-type", "image/png"))
        elif url.path == "/message.html":
            self.__send_static_file('message.html', ("Content-type", 'text/html'))
        else:
            self.__send_static_file('error.html', ("Content-type", "text/html"), 404)

    def do_POST(self):
        #print("POST")
        url = self.__parse_url()
        if url.path == "/message":
            data = self.__read_message_form()
            self.__send_data_to_storage(data)
            self.__redirect('/message.html')
        else:
            self.__send_static_file('error.html', ("Content-type", "text/html"), 404)

    def __send_static_file(self, filename, header, status=200):
        self.send_response(status)
        self.send_header(header[0], header[1])
        self.end_headers()
        with open(f"{ROOT_STATIC_FOLDER}/{filename}", 'rb') as fd:
            self.wfile.write(fd.read())

    def __redirect(self, location):
        self.send_response(302)
        self.send_header('Location', location)
        self.end_headers()

    def __send_data_to_storage(self, data):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((SOCKET_HOST, SOCKET_PORT))
        client.send(json.dumps(data).encode("utf-8"))
        response = client.recv(1024).decode('utf-8')
        print(response)
        client.close()

    def __read_message_form(self):
        content_length = self.rfile.read(int(self.headers['Content-Length']))
        data_parse = urllib.parse.unquote_plus(content_length.decode())
        return {key: value for key, value in [element.split('=') for element in data_parse.split('&')]}


class WebServer:
    def __init__(self,
            port,
            root_static_folder,
            socket_host='localhost',
            socket_port=3000):
        self.port = port
        self.root_static_folder = root_static_folder
        self.socket_port = socket_port
        self.socket_host = socket_host
        self.__write_global_vars()

    def __write_global_vars(self):
        global ROOT_STATIC_FOLDER
        global SOCKET_HOST
        global SOCKET_PORT
        ROOT_STATIC_FOLDER = self.root_static_folder
        SOCKET_HOST = self.socket_host
        SOCKET_PORT = self.socket_port

    def run(self):
        server_address = ('', self.port)
        http = HTTPServer(server_address, HttpHandler)
        try:
            http.serve_forever()
        except KeyboardInterrupt:
            http.server_close()
