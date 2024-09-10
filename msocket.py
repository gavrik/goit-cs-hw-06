import socket
import threading
from pymongo import MongoClient
from datetime import datetime

from webserver import SOCKET_HOST, SOCKET_PORT

class MongoDB:
    def __init__(self, connection_string, mongo_db):
        self.connection_string = connection_string
        self.mongo_db = mongo_db
        self.connection()

    def connection(self):
        self.client = MongoClient(self.connection_string)
        self.db = self.client[self.mongo_db]
        self.collection = self.db['form_message']

    def write_message(self, data):
        data["date"] = datetime.now()
        res = self.collection.insert_one(data)
        print("Inserted document_id: ", res.inserted_id)
    def close(self):
        self.client.close()

class SocketServer:
    def __init__(self,
            socket_host='localhost',
            socket_port=3000,
            mongo_connection_string=None,
            mongo_db=None):
        self.socket_host = socket_host
        self.socket_port = socket_port
        self.mongo_connection_string = mongo_connection_string
        self.mongo_db = mongo_db
        self.server = None
        self.mongodb = None
        self.build()

    def __write_global_vars(self):
        global SOCKET_HOST
        global SOCKET_PORT
        SOCKET_HOST = self.socket_host
        SOCKET_PORT = self.socket_port

    def build(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.socket_host, self.socket_port))
        self.server.listen()

    def handle_client(self, client, address):
        request = client.recv(1024).decode("utf-8")
        print("request: ", request)
        self.mongodb = MongoDB(self.mongo_connection_string, self.mongo_db)
        self.mongodb.write_message(request)
        self.mongodb.close()
        client.send("OK".encode("utf-8"))
        client.close()

    def run(self):
        while True:
            client, address = self.server.accept()
            print(f"Connection from {str(address)}")
            cthread = threading.Thread(target=self.handle_client, args=(client, address))
            cthread.start()
