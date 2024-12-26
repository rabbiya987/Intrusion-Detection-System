import socket
import re
HOST = 'localhost'
PORT = 9090

intrusive_pattern = re.compile(r'\b(sudo|rm -rf|drop table|shutdown|nmap|ping)\b', re.IGNORECASE)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print("=====================================================")
    print(f"|             CLIENT CONNECTED WITH PORT {PORT}             |")
    print("=====================================================")
    while True:
        try:
            message = input("Enter a command: ")
            if message.lower() == 'exit':
                break
            
            if intrusive_pattern.search(message):
                print("Intrusive command detected. Command not sent.")
            else:
                s.sendall(message.encode())
                data = s.recv(1024)
                print("Command sent successfully.")
                print(f"Received from server: {data.decode()}")

        except KeyboardInterrupt:
            print("\nExiting client...")
            break