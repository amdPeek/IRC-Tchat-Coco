from tkinter import *
import tkinter.font as tkFont
import sys
import socket 
import threading

class App:
    def __init__(self):     
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

        # Créer la Listbox pour les canaux
        self.channel_listbox = Listbox(self.root, bg=bg_color, fg=fg_color)
        self.channel_listbox.place(x=60, y=70, width=140, height=600)

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
        self.user_listbox = Listbox(self.root, bg=bg_color, fg=fg_color)
        self.user_listbox.place(x=900, y=70, width=140, height=600)

        # Labels avec le thème sombre
        label_style = {"fg": fg_color, "justify": "center", "bg": "black"}
        GLabel_465 = Label(self.root, text="Channels", **label_style)
        GLabel_465.place(x=90, y=20, width=70, height=25)

        GLabel_774 = Label(self.root, text="Users", **label_style)
        GLabel_774.place(x=930, y=30, width=70, height=25)


        self.client_socket = socket.socket() 
        self.client_socket.connect((socket.gethostname(), 5500)) 

        self.listen_thread = threading.Thread(target=self.listen)
        self.listen_thread.start()    

        self.root.mainloop()

        self.client_socket.close() # TO-DO : à bouger dans une fonction appropriée 

    def send_cmd(self):
        texte_saisi = self.entry_cmd.get()
        self.entry_cmd.delete(0, 'end')
        self.client_socket.send(texte_saisi.encode()) 

    def insert_chat_area(self,data):
        self.chat_area.config(state="normal")
        self.chat_area.insert(END, data + "\n")
        self.chat_area.config(state="disabled")

    def on_closing(self):
        self.client_socket.close()
        self.root.destroy()

    def listen(self):
        while True:
            data = self.client_socket.recv(1024).decode()
            if not data: 
                return

            #parsing incoming data
            my_str = str(data)
            print(my_str)
            self.insert_chat_area(my_str)


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("usage : gui_client.py <nickname>")
    else:
        app = App()

        
