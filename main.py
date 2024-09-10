from webserver import WebServer
from msocket import SocketServer, MongoDB
from time import sleep
import signal
import os
import multiprocessing as mp

PROCESS = []

def read_env(env_name):
    return os.environ[env_name]

def run_webserver():
    print("Starting web server")
    web = WebServer(
        port = int(read_env("WEBSERVER_PORT")),
        root_static_folder = read_env("STATIC_FOLDER_PATH"),
        socket_host = read_env("SOCKET_HOST"),
        socket_port = int(read_env("SOCKET_PORT"))
    )
    web.run()

def run_socket():
    print("Starting socket server")
    soc = SocketServer(
        socket_host = read_env("SOCKET_HOST"),
        socket_port = int(read_env("SOCKET_PORT")),
        mongo_connection_string = read_env("MONGO_CONN_STR"),
        mongo_db = read_env("MONGO_DB")
    )
    soc.run()

def handle_signal(signum, frame):
    global PROCESS
    print("Terminate signal was raised!")
    for pid in PROCESS:
        if pid.is_alive():
            print("Terminate: ", pid.name)
            pid.terminate()


if __name__ == "__main__":
    PROCESS = []

    PROCESS.append(mp.Process(target=run_webserver, name='web_server'))
    PROCESS[0].start()
    sleep(1)
    PROCESS.append(mp.Process(target=run_socket, name="socket_server"))
    PROCESS[1].start()
    sleep(1)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    PROCESS[0].join()
    PROCESS[1].join()
