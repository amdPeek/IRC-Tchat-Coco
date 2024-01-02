#!/usr/bin/python3

import socket
import sys
import time, threading
import pickle


class User:
	def __init__(self,conn,addr,nickname):
		self.conn = conn
		self.addr = addr
		self.nickname = nickname

	def set_nickname(self,nickname):
		self.nickname = nickname

	def get_conn(self):
		return self.conn

	def get_addr(self):
		return self.addr

	def get_nickname(self):
		return self.nickname

class Channel:
	def __init__(self,name_channel):
		self.name_channel = name_channel
		self.user_list = []

	def get_user_list(self):
		return self.user_list

	def add_user(self,user):
		print(f"  >>>> {user.get_nickname()} has been added to the {self.name_channel} channel")
		self.user_list.append(user)

	def send_channel(self,data):
		for user in self.user_list:
			try:
				serialized_data = pickle.dumps(data)
				user.get_conn().send(serialized_data)
			except Exception as e:
				print(e)
				#print(f"  >>>> Broken pipe for user {user.get_nickname()}")

class Server:
	def __init__(self, server_name):
		self.server_name = server_name
		self.ip = "127.0.0.1"
		self.port = 5500
		self.socket_server = None
		self.list_current_user = [User(None,None,"users_list")]	 #just to init our keys for the client part
		self.channel_list = {}
		self.channel_list["channels_list"] = None 			#just to init our keys for the client part
		self.server_object = User(None,None,"SERVER")

	def print_current_users(self):
		self.prRed(f" >>>> [LOG] There are {len(self.list_current_user) - 1} connected users")
		threading.Timer(30, self.print_current_users).start()

	def send_channels(self):
		if len(self.channel_list.keys()) > 1:
			list_to_send = list(self.channel_list.keys())
			#print(f"Sending {list_to_send}")

			for u in self.list_current_user:
				self.send_all(self.server_object,list_to_send)

		threading.Timer(0.5, self.send_channels).start()	

	def send_users(self):
		if len(self.list_current_user) > 1:
			list_to_send = [user.nickname for user in self.list_current_user] 
			#print(f"Sending {list_to_send}")

			for u in self.list_current_user:
				self.send_all(self.server_object,list_to_send)

		threading.Timer(0.5, self.send_users).start()

	def send_all(self,user,data,channel="default"):
		if isinstance(data, list):
			(self.channel_list[channel]).send_channel(data) 
		elif isinstance(data, str):
			(self.channel_list[channel]).send_channel(f"{user.get_nickname()} : {data}") 

	def send_private(self,user,data):
		serialized_data = pickle.dumps(data)
		user.get_conn().send(serialized_data)

	def parse_command(self,user,data):
		cmd = data.split(" ")
		
		if len(cmd) == 0:
			self.send_private(user,"please provide a correct command")
			return

		match cmd[0]:
			case "/setnickname":
				print(f"  >>>> New user {cmd[1]}")

				self.send_all(self.server_object,f"  >>>> New user {cmd[1]}","default")

				#set the nickname
				user.set_nickname(cmd[1])

				#by default we add all users to the default channel
				(self.channel_list["default"]).add_user(user)

				self.send_private(user,f" >>>> You succesfully connected to {self.server_name}")
			case "/away":
				pass
			case "/help":
				pass
			case "/invite":
				pass
			case "/join":
				pass
			case "/list":
				pass
			case "/msg":
				if len(cmd) == 1:
					self.send_private(user,"Incorrect syntax")
				else:
					if (cmd[1])[0] == '[' and (cmd[1])[len(cmd[1])-1] == ']': #specifying a canal
					   	canal_name = cmd[1:-1]
					   	self.send_all(user,"//TO-DO",canal_name)
					else: #messaging in the default channel 
						msg = " ".join(cmd[1:])
						self.send_all(user,msg,"default")

			case "/names":
				pass
			case _:
				self.send_private(user,"This command does not exists...") 

	def create_channel(self,name):
		self.channel_list[name] = Channel(name)
		self.prGreen(f" >>>> The {name} channel has been created")

	def handle_user(self,user):
		
		while True:
			data = user.get_conn().recv(1024).decode()
			if not data:
				print(f"  >>>> {user.get_addr()}:({user.get_nickname()}) has left")
				self.list_current_user.remove(user)
				self.send_all(User(None,None,"SERVER"),f"  >>>> {user.get_addr()} has left","default")
				break
			self.parse_command(user,data)
			

	def start_server(self):
		self.socket_server = socket.socket()
		self.socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.socket_server.bind((socket.gethostname(),5500))
		self.prGreen('''

			  _				___					___  _   _ 
			 /   _   _  _ __ |  _ |_   _. _|_ __ |  |_) /  
			 \_ (_) (_ (_)   | (_ | | (_|  |_   _|_ | \ \_ 
											   

			''')
		self.prGreen(" >>>> Server Started ")

		#create default channel
		self.create_channel("default")

		self.socket_server.listen(5)
		#print the current users
		self.print_current_users()

		self.send_users()
		self.send_channels()

		while True:
			#receiving conn params
			tmp_conn, tmp_addr = self.socket_server.accept()
			#adding him to the user list
			new_user = User(tmp_conn,tmp_addr," ")
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