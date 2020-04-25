import sys
from time import sleep
from sys import stdin, exit
from random import randint

from tkinter import *
from tkinter import simpledialog, messagebox

from PodSixNet.Connection import connection, ConnectionListener

from gamewindow import *

DEAD = -1
IN_GAME = 2

class Client(ConnectionListener):

    def __init__(self, host, port):
        #SETUP GUI
        self.tableWindow = Tk()
        self.tableWindow.title("Witcher Tornament")
        self.tableWindow.protocol("WM_DELETE_WINDOW", self.quit)
        self.tableWindow.withdraw()

        self.playersFrame = LabelFrame(self.tableWindow, text="Joueurs")
        self.scoreFrame = LabelFrame(self.tableWindow, text="Scores")

        self.scoreList = Listbox(self.scoreFrame)

        self.playersFrame.pack(side=LEFT, fill=BOTH, expand=True)
        self.scoreFrame.pack(side=RIGHT, fill=BOTH, expand=True)
        self.scoreList.pack()

        #GAME WINDOW
        self.game = None

        # GET A USERNAME
        nickname = ""
        while nickname in [None, ""]:
            nickname = simpledialog.askstring("Nom", "Entrez votre nom : ").rstrip("\n")
        self.nickname = nickname

        self.tableWindow.title(f"Witcher Tornament - {self.nickname}")
        self.tableWindow.deiconify()

        # SETUP CLIENT
        self.Connect((host, port))
        self.state = INITIAL
        print("Client started")

        connection.Send({"action": "nickname", "nickname": self.nickname})
        self.Loop()

    def Loop(self):
        connection.Pump()
        self.Pump()

    def quit(self):
        self.tableWindow.destroy()
        self.state = DEAD

    def Network_connected(self, data):
        print("You are now connected to the server")
  
    def Network_start(self, data):
        self.askPlayersList()

        while self.state != DEAD:   
            self.tableWindow.update()
            self.Loop()
            sleep(0.001)
        exit()    

    def askPlayersList(self):
        self.Send({"action": "playersList"})

    def askMatch(self, nickname):
        if messagebox.askokcancel("Match", f"Voulez vous défier {nickname} ?"):
            self.Send({"action": "askMatch", "nickname": nickname})

    def Network_askMatch(self, data):
        if messagebox.askokcancel("Match", f"{data['nickname']} vous défie\nVoulez vous jouer contre lui ?"):
            self.Send({"action": "matchAccepted", "nickname": data["nickname"]})
        else: self.Send({"action": "matchRefused", "nickname": data["nickname"]})

    def Network_matchRefused(self, data):
        messagebox.showinfo("Match refusé", f"{data['nickname']} ne veut pas jouer avec vous...")

    def Network_launchGame(self, data):
        first = data["first"]
        self.game = GameWindow(self, first)
        self.askPlayersList()
 
    def Network_newPoint(self, data):
        self.game.newPoint(data)

    def Network_newMove(self, data):
        self.game.newMove(data)

    def Network_win(self, data):
        self.Send({"action": "win"})
        self.game.window.destroy()
        print("Vous avez gagné !")
        messagebox.showinfo("Gagné", "Vous avez gagné !")

        self.askPlayersList()

    def Network_playersList(self, data):
        playersList = data["playersList"]

        for child in self.playersFrame.winfo_children():
            child.destroy()

        print("J'ai reçu les joueus :")
        for i in range(len(playersList)):
            name, free = playersList[i]
            print(f"\t {name}, {free}")
            Label(self.playersFrame, text=name).grid(row=i, column=0)
            Label(self.playersFrame, text=" libre !" if free else " en  match...").grid(row=i, column=1)
            if free and name != self.nickname:
                print(f"Je met un bouton à {name}")
                nickname = name
                Button(self.playersFrame, text="Défier !", command=lambda: self.askMatch(nickname)).grid(row=i, column=2) #y'a un bullshit ici jsp pq

    def Network_error(self, data):
        print('error:', data['error'][1])
        connection.Close()
    
    def Network_disconnected(self, data):
        print('Server disconnected')
        exit()

if len(sys.argv) != 2:
    print("Please use: python3", sys.argv[0], "host:port")
    print("e.g., python3", sys.argv[0], "localhost:31425")
    sys.exit(1)

host, port = sys.argv[1].split(":")
client = Client(host, int(port))
sleep(0.5)
# first loop to say to the server that I exist
client.Loop()

