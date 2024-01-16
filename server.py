#!/usr/bin/python3

import socket
import sys
import time, threading
import pickle
import pyfiglet
import random


class User:
	def __init__(self,conn,addr,nickname):
		self.conn = conn
		self.addr = addr
		self.nickname = nickname
		self.away = False
		self.away_message = f"{self.get_nickname} is away, he'll be back soon !"

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
		self.recent_msg = [f"{self.name_channel}",f"welcome to the {self.name_channel} channel !"]
		self.key = ""

	def get_recent_msg(self):
		return self.recent_msg

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
			except:
				#print(e)
				print(f"  >>>> Broken pipe for user {user.get_nickname()}")

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
			list_to_send = [ (user.nickname,user.away) for user in self.list_current_user[1:]]
			list_to_send.insert(0, "users_list") 
			#print(f"Sending {list_to_send}")

			for u in self.list_current_user:
				self.send_all(self.server_object,list_to_send)

		threading.Timer(0.5, self.send_users).start()

	def send_all(self,user,data,channel="default"):
		if isinstance(data, list):
			(self.channel_list[channel]).send_channel(data) 
		elif isinstance(data, str):
			(self.channel_list[channel]).send_channel(f"{channel}:{user.get_nickname()}:{data}") 

	def send_private(self,user,data):
		serialized_data = pickle.dumps(data)
		user.get_conn().send(serialized_data)

	def parse_command(self,user,data):
		words = data.split(" ")
		cmd = [word for word in words if word]
		
		if len(cmd) == 0:
			self.send_private(user,"please provide a correct command")
			return

		match cmd[0]:
			case "/request_channel":
				requested_channel = cmd[1]
				print(f"  >>>> {user.get_nickname()} requesting the {requested_channel} channel")
				self.send_private(user,self.channel_list[requested_channel].get_recent_msg())
			case "/setnickname":
				print(f"  >>>> New user {cmd[1]}")

				self.send_all(self.server_object,f"  >>>> New user {cmd[1]}","default")

				#set the nickname
				user.set_nickname(cmd[1])

				#by default we add all users to the default channel
				(self.channel_list["default"]).add_user(user)

				self.send_private(user,f" >>>> You succesfully connected to {self.server_name}")
			case "/away":
				if len(cmd) == 1:
					user.away = not user.away
				elif len(cmd) == 2:
					user.away = not user.away
					user.away_message = cmd[1]
				else:
					self.send_private(user,"Syntax error : /away <OPT:away_msg>")
			case "/help":
				help_msg = """
				away [message]\n
				/help\n
				/invite <channel>\n
				/join <channel>\n
				/list\n
				/msg [channel|nickname] message\n
				/names [channel]\n
				"""
				self.send_private(user,help_msg)
			case "/invite":
				pass
			case "/join":
				if len(cmd) == 2: #/join <channel_name>
					channel_name = cmd[1]
					if channel_name in list(self.channel_list.keys()):
						self.send_private(user,f"Error : the {channel_name} channel already exists")
					else:
						self.create_channel(channel_name)
						self.send_all(self.server_object,f"the {channel_name} channel has been created")
						self.channel_list[channel_name].add_user(user)
				elif len(cmd) == 3: #/join <channel_name> <key>	
					pass
				else:
					self.send_private(user,"Syntax error : /join <canal_name> <OPT:key>")
			case "/list":
				list_channel_str = '\n'.join(list(self.channel_list.keys())[1:])
				final_str = f"\nThe current channel's list :\n{list_channel_str}"
				self.send_private(user,final_str)
			case "/msg":
				if len(cmd) == 1:
					self.send_private(user,"Incorrect syntax")
				else:
					if (cmd[1])[0] == '[' and (cmd[1])[len(cmd[1])-1] == ']': #specifying a canal or a user
					   #first step is to check if wether it's a channel of a user
					   arg = (cmd[1])[1:-1]

					   if arg in self.channel_list.keys(): #send it to a channel
						   channel_name = arg
						   msg = " ".join(cmd[2:])
						   self.channel_list[channel_name].recent_msg.append(f"{user.get_nickname()} : {msg}")
						   print(self.channel_list[channel_name].recent_msg)
						   self.send_all(user,msg,channel_name)
					   elif arg in [user.nickname for user in self.list_current_user[1:]]: #send it to a user
					   	   user_target_str = arg 
					   	   msg = " ".join(cmd[2:])
					   	   list_to_send = ["FROM",user.get_nickname(),msg]

					   	   if user_target_str == user.get_nickname():
					   	        pass 	
					   	   else:
						   	   #find the user
						   	   user_target = None
						   	   for u in self.list_current_user[1:]:
						   	   		if u.get_nickname() == user_target_str:
						   	   			user_target = u
						   	   			break
						   	   self.send_private(u,list_to_send)
					   else:
					       self.send_private(user,f"{arg} is neither a channel name nor a user in the server ...")


					else: #messaging in the default channel 
						msg = " ".join(cmd[1:])
						self.channel_list["default"].recent_msg.append(f"{user.get_nickname()} : {msg}")
						print(self.channel_list["default"].recent_msg)
						self.send_all(user,msg,"default")

			case "/names":
				if len(cmd) > 1: #expecting specifying a channel
					channel_name = cmd[1]

					#checking if it exists
					if channel_name in list(self.channel_list.keys()):
						channel_obj = self.channel_list[channel_name]
						list_to_send = '\n'.join([user.nickname for user in channel_obj.user_list])
						list_to_send_str =  f"\nAll user in the {channel_name} :\n{list_to_send}"
						self.send_private(user,list_to_send_str)
					else:
						self.send_private(user,f"\nThe {channel_name} does not exists ...\n")
				else: #we print everything (the server list..)
					list_to_send = '\n'.join([ user.nickname for user in self.list_current_user[1:]])
					list_to_send_str = f"\nAll current users :\n{list_to_send}"
					self.send_private(user,list_to_send_str)

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
				addr = user.get_addr()

				#removing him from the server list
				self.list_current_user.remove(user)

				#and also in every channel he used to tchat
				for channel in self.channel_list.values():
					if channel != None:
						for channel_user in channel.get_user_list():
							if channel_user.get_nickname() == user.get_nickname():
								channel.user_list.remove(channel_user)

				self.send_all(User(None,None,"SERVER"),f"  >>>> {addr} has left","default")
				break
			self.parse_command(user,data)
			

	def start_server(self):
		self.socket_server = socket.socket()
		self.socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.socket_server.bind((socket.gethostname(),5500))

		ascii_banner = pyfiglet.figlet_format(f"{self.server_name}-Tchat-IRC")
		self.prGreen(ascii_banner)

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