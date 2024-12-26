import socket
import logging
import re
import threading
import sys
import signal

# 1. Activity logger (INFO level)
activity_logger = logging.getLogger('activity')
activity_logger.setLevel(logging.INFO)
activity_file_handler = logging.FileHandler('activity.log')
activity_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
activity_file_handler.setFormatter(activity_formatter)
activity_logger.addHandler(activity_file_handler)

# 2. Error logger (ERROR level)
error_logger = logging.getLogger('error')
error_logger.setLevel(logging.ERROR)
error_file_handler = logging.FileHandler('error.log')
error_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
error_file_handler.setFormatter(error_formatter)
error_logger.addHandler(error_file_handler)

#creating a pattern for intrusive commands
intrusive_pattern = re.compile(r'\b(sudo|rm -rf|drop table|shutdown|nmap|ping)\b', re.IGNORECASE)

# Define a list of intrusive commands
intrusive_commands = [
    "sudo", 
    "su", 
    "root", 
    "rm -rf", 
    "rm -r", 
    "del /f /q /s", 
    "format", 
    "shutdown", 
    "reboot", 
    "drop table", 
    "truncate table", 
    "delete from", 
    "insert into", 
    "update", 
    "alter table", 
    "grant all privileges", 
    "net user", 
    "whoami /priv", 
    "tasklist /v", 
    "ipconfig /all", 
    "ping", 
    "traceroute", 
    "telnet", 
    "netcat", 
    "nmap" 
]

def handle_client(conn, addr):
    #creating IDs for each client.
    thread_id = threading.get_ident()
    activity_logger.info(f"Connection established with {addr} - Thread ID: {thread_id}")
    print(f"\n\n==============================>Connection established with {addr} - Thread ID: {thread_id} <==============================")
    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break
            print(f"Received command from {addr} - Thread ID: {thread_id}: {data}")

            is_intrusive = False
            for command in intrusive_commands:
                if command in data.lower():
                    is_intrusive = True
                    break
            #Checking if the command id intrusive
            if is_intrusive or intrusive_pattern.search(data):
                error_logger.error(f"Intrusive command detected from {addr[0]}:{addr[1]}  - Thread ID: {thread_id} - Command: {data}")
                conn.sendall(b"Intrusive command.\n") 
            else:
                activity_logger.info(f"Received command from {addr}: {data}")
                conn.sendall(b"Command executed successfully.\n") 

        except Exception as e:
            print(f"Error handling client: {e}")
            break
    conn.close()
    activity_logger.info(f"Connection closed with {addr}")
    print(f"\n\n=========================> Connection closed with {addr} <=========================")

def signal_handler(signal,frame):
    print("\nServer is shutting down...")
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    host = 'localhost'
    port = 9090

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        activity_logger.info(f"Server listening on {host}:{port}")
        print(f"\n\n==============================> Server listening on {host}:{port} <==============================") 
        while True:
            conn, addr = s.accept()
            client_thread=threading.Thread(target=handle_client, args=(conn,addr))
            client_thread.start()

if __name__ == '__main__':
    main()