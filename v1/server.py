import socket
import sys
import time, threading


class User:
	def __init__(self,conn,addr,nickname):
		self.conn = conn
		self.addr = addr
		self.nickname = nickname

	def get_conn(self):
		return self.conn

	def get_addr(self):
		return self.addr

	def get_nickname(self):
		return self.nickname

class Server:
	def __init__(self, server_name):
		self.server_name = server_name
		self.ip = "127.0.0.1"
		self.port = 5500
		self.socket_server = None
		self.list_current_user = []

	def print_current_users(self):
		self.prRed(f" >>>> [LOG] There are {len(self.list_current_user)} connected users")
		threading.Timer(30, self.print_current_users).start()

	def handle_user(self,user):
		print(" >>>> New user")

		while True:
			data = user.get_conn().recv(1024).decode()
			if not data:
				print(f"{user.get_addr()} has left")
				break
			print(f"{user.get_addr()} : {str(data)}")

	def start_server(self):
		self.socket_server = socket.socket()
		self.socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.socket_server.bind((socket.gethostname(),5500))
		self.prGreen('''

			  _			 ___				 ___  _   _ 
			 /   _   _  _ __ |  _ |_   _. _|_ __ |  |_) /  
			 \_ (_) (_ (_)   | (_ | | (_|  |_   _|_ | \ \_ 
											   

			''')
		self.prGreen(" >>>> Server Started ")
		self.socket_server.listen(5)

		self.print_current_users()

		while True:
			#receiving conn params
			tmp_conn, tmp_addr = self.socket_server.accept()
			#adding him to the user list
			new_user = User(tmp_conn,tmp_addr,"nick")
			self.list_current_user.append(new_user)
			#we handle him with a thread
			t = threading.Thread(target=self.handle_user,args=(new_user,))
			t.start()

			


	def prGreen(self,skk): 
		print('''\033[92m {}\033[00m'''.format(skk))

	def prRed(self,skk): 
		print('''\033[91m {}\033[00m''' .format(skk))

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("usage : server.py <server_name>")
	else:
		server_name = sys.argv[1]
		
		server = Server(server_name)
		server.start_server()