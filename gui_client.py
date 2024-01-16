#!/usr/bin/python3

from tkinter import *
import tkinter.font as tkFont
import sys
import socket 
import threading
import pickle


class App:
    def __init__(self,nickname):     
        # vars to understand the server
        self.nickname = nickname
        self.current_channel = "default"
        self.list_channels = None
        self.current_PM = {}

        # setting title
        self.root = Tk()
        self.root.title("IRC client")
        self.root.configure(background='black')
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # setting window size
        width = 1100
        height = 768
        screenwidth = self.root.winfo_screenwidth()
        screenheight = self.root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.root.geometry(alignstr)
        self.root.resizable(width=False, height=False)

        # Couleurs pour le thème sombre
        bg_color = "#333333"
        fg_color = "#ffffff"
        entry_bg_color = "#555555"
        entry_fg_color = "#ffffff"
        button_bg_color = "#666666"
        button_fg_color = "#ffffff"

        listbox_style = {"bg": bg_color, "fg": fg_color, "selectbackground": "#ffA500", "selectforeground": "black", "font": ("Helvetica", 12), "justify": "center"}

        # Créer la Listbox pour les canaux
        self.channel_listbox = Listbox(self.root,**listbox_style)
        self.channel_listbox.place(x=60, y=70, width=140, height=600)
        self.channel_listbox.bind("<ButtonRelease-1>", self.request_channel)

        # Créer la zone de chat avec une scrollbar
        self.chat_area = Text(self.root, height=35, width=75, bg=bg_color, fg=fg_color)
        self.chat_area.place(x=250, y=70)
        self.chat_area.config(state="disabled")

        # Créer la scrollbar et la lier à la zone de chat
        scrollbar = Scrollbar(self.root, command=self.chat_area.yview, bg="#ff9900")
        scrollbar.place(x=855, y=70, height=600)
        self.chat_area.config(yscrollcommand=scrollbar.set)

        # Créer le champ d'entrée
        self.entry_cmd = Entry(self.root, bg=entry_bg_color, fg=entry_fg_color)
        self.entry_cmd.place(x=240, y=690, width=596, height=30)

        # Créer le bouton d'envoi
        self.validate_cmd = Button(self.root, bg=button_bg_color, fg=button_fg_color, text="Send", command=self.send_cmd)
        self.validate_cmd.place(x=850, y=690)

        # Créer la Listbox pour les utilisateurs
        self.user_listbox = Listbox(self.root,**listbox_style)
        self.user_listbox.place(x=900, y=70, width=140, height=600)

        # Labels avec le thème sombre
        label_style = {"fg": fg_color, "justify": "center", "bg": "black"}
        GLabel_465 = Label(self.root, text="Channels", **label_style)
        GLabel_465.place(x=90, y=20, width=70, height=25)

        GLabel_774 = Label(self.root, text="Users", **label_style)
        GLabel_774.place(x=930, y=20, width=70, height=25)


        # Créer un label pour savoir dans quel salon on se situe
        self.label_current_channel = Label(self.root,text=f"current channel : {self.current_channel}",**label_style)
        self.label_current_channel.place(x=500,y=20)


        self.client_socket = socket.socket() 
        self.client_socket.connect((socket.gethostname(), 5500)) 

        self.listen_thread = threading.Thread(target=self.listen)
        self.listen_thread.start()    

        #send the username
        self.send_nickname()

        self.root.mainloop()

        self.client_socket.close() # TO-DO : à bouger dans une fonction appropriée 

    def request_channel(self,event):
        selected_item_index = self.channel_listbox.curselection()
        if selected_item_index:
            selected_channel = self.channel_listbox.get(selected_item_index[0])

            if selected_channel != self.current_channel:
                to_send = f"/request_channel {selected_channel}"
                self.client_socket.send(to_send.encode())
                self.current_channel = selected_channel
                self.label_current_channel.configure(text=f"current channel : {self.current_channel}")



    def send_nickname(self):
        to_send = f"/setnickname {self.nickname}"
        self.client_socket.send(to_send.encode())

    def update_user_list(self,newlist):
        self.user_listbox.delete(0, END)
        idx = 0
        for e in newlist[1:]:
            self.user_listbox.insert(END, e[0])
            if not e[1]:
                self.user_listbox.itemconfigure(idx, bg="#00aa00", fg="#fff")
            else:
                self.user_listbox.itemconfigure(idx, bg="#ffA500", fg="#fff")
            idx+=1


    def update_channel_list(self,newlist):
        self.channel_listbox.delete(0, END)
        for e in newlist[1:]:
            self.channel_listbox.insert(END, e)


    def send_cmd(self):
        texte_saisi = self.entry_cmd.get()
        self.entry_cmd.delete(0, 'end')
        self.client_socket.send(texte_saisi.encode()) 

    def insert_chat_area(self,data,color="white"):
        self.chat_area.config(state="normal")
        if isinstance(data,list):
            self.chat_area.delete(1.0,END)
            for msg in data:
                self.chat_area.insert(END, str(msg) + "\n")
        else:
            self.chat_area.insert(END, str(data) + "\n",color)
            self.chat_area.tag_configure(color, foreground=color)
        self.chat_area.config(state="disabled")

    def on_closing(self):
        self.client_socket.close()
        self.root.destroy()

    def listen(self):
        while True:
            data = self.client_socket.recv(1024)
            if not data: 
                return

            try:
                if isinstance(data, bytes):
                    received_data = pickle.loads(data)
                    if isinstance(received_data, list):

                        match received_data[0]:
                            case "channels_list":
                                #print("J'ai reçu la liste des channels")
                                self.list_channels = received_data
                                self.update_channel_list(received_data)
                            case "users_list":
                                #print("J'ai reçu la liste des users")
                                #print(received_data)
                                self.update_user_list(received_data)
                            case "FROM":
                                #case of a private message
                                sender = received_data[1]
                                msg = received_data[2]

                                #check if it's the first interaction
                                if sender not in list(self.current_PM.keys()):
                                    self.current_PM[sender] = [msg]
                                else:
                                    self.current_PM[sender].append(msg)

                                self.insert_chat_area(f"PM from [{sender}] : {msg}",'orange')
                                print(received_data)

                            case _:
                                if self.list_channels != None:
                                    if received_data[0] in self.list_channels:
                                        print(f"j'ai reçu les logs du salon {received_data[0]}")
                                        print(received_data)
                                        self.insert_chat_area(received_data)
                                    else:
                                        print("this list is not supported")

                    elif isinstance(received_data, str):
                        splitted_data = received_data.split(":")
                        if self.list_channels is not None:
                            if splitted_data[0] in self.list_channels:
                                #print(f"message pour {splitted_data[0]}")
                                if splitted_data[0] == self.current_channel:
                                    self.insert_chat_area(" ".join(splitted_data[1:]))
                            else:
                                self.insert_chat_area(" ".join(splitted_data))
                                #print(splitted_data)
                                #print("J'ai reçu un message pour un salon qui n'existe pas ...")
                    else:
                        print(received_data)
                else:
                    print("Données reçues non valides. Attendez-vous à des bytes.")
            except pickle.UnpicklingError:
                print("Erreur lors de la désérialisation du message.")
     
            

       

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("usage : gui_client.py <nickname>")
    else:
        app = App(sys.argv[1])

        
