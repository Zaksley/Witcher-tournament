import sys
from time import sleep
from sys import stdin, exit
from random import randint

from tkinter import *
from tkinter import simpledialog, messagebox

from PodSixNet.Connection import connection, ConnectionListener

from gamewindow import *

class Client(ConnectionListener):

    def __init__(self, host, port):
        #SETUP GUI
        self.tableWindow = Tk()
        self.tableWindow.title("Witcher Tornament")
        self.tableWindow.protocol("WM_DELETE_WINDOW", self.quit)
        self.tableWindow.wm_minsize(400, 300)
        self.tableWindow.withdraw()

        self.playersFrame = LabelFrame(self.tableWindow, text="Tableau des scores")
        self.playersFrame.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)

        #GAME WINDOW
        self.game = None
        self.state = WAITING

        # GET A USERNAME
        nickname = ""
        while nickname in [None, ""]:
            nickname = simpledialog.askstring("Pseudo", "Entrez votre pseudo : ").rstrip("\n")
        self.nickname = nickname

        self.tableWindow.title(f"Witcher Tornament - {self.nickname}")
        self.tableWindow.deiconify()

        # SETUP CLIENT
        self.Connect((host, port))
        print("Client started")

        connection.Send({"action": "nickname", "nickname": self.nickname})
        self.Loop()

    def Loop(self):
        connection.Pump()
        self.Pump()

    def quit(self):
        if self.state == IN_GAME:
            return

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

    def Network_tooHigh(self, data):
        messagebox.showerror("Erreur", "La différence de rating entre vous et votre adversaire est supérieure à 300 !")

    def Network_tornamentStarted(self, data):
        messagebox.showinfo("Tournoi", "Le tournoi a commencé !\nVous pouvez maintenant défier des adversaires")

    def Network_tornamentNotStarted(self, data):
        messagebox.showerror("Erreur", "Attendez, le tournoi n'a pas ecnore commencé !")

    def Network_alreadyStarted(self, data):
        messagebox.showerror("Erreur", "Le tournoi a déjà commencé !")
        exit()

    def Network_wrongNickname(self, data):
        messagebox.showerror("Erreur", f"Le pseudo {self.nickname} est déjà pris !")
        exit()

    def askPlayersList(self):
        self.Send({"action": "playersList"})

    def askMatch(self, nickname):
        if messagebox.askokcancel("Match", f"Voulez vous défier {nickname} ?"):
            self.Send({"action": "askMatch", "nickname": nickname})

    def Network_askMatch(self, data):
        if self.state == IN_GAME:
            return

        if not data["canRefuse"]:
            messagebox.showinfo("Match", f"{data['nickname']} vous défie !")
            self.Send({"action": "matchAccepted", "nickname": data["nickname"]})
            return

        if messagebox.askokcancel("Match", f"{data['nickname']} vous défie\nVoulez vous jouer contre lui ?"):
            self.Send({"action": "matchAccepted", "nickname": data["nickname"]})
        else: self.Send({"action": "matchRefused", "nickname": data["nickname"]})

    def Network_matchRefused(self, data):
        messagebox.showinfo("Match refusé", f"{data['nickname']} ne veut pas jouer avec vous...")

    def Network_launchGame(self, data):
        first = data["first"]
        nickname = data["nickname"]
        self.game = GameWindow(self, first, nickname)
        self.askPlayersList()
        self.state = IN_GAME
 
    def Network_newPoint(self, data):
        self.game.newPoint(data)

    def Network_newMove(self, data):
        self.game.newMove(data)

    def Network_win(self, data):
        self.Send({"action": "win"})

        self.game.window.destroy()
        self.state = WAITING

        print("Vous avez gagné !")
        messagebox.showinfo("Gagné", "Vous avez gagné !")

        self.askPlayersList()

    def Network_playersList(self, data):
        playersList = data["playersList"]
        playersList.sort(key=lambda x: x[2], reverse=True)

        for child in self.playersFrame.winfo_children():
            child.destroy()

        print("J'ai reçu les joueus :")
        for i in range(len(playersList)):
            name, free, rating = playersList[i]
            print(f"\t {name}, {free}")
            Label(self.playersFrame, text=f"{i+1} - {rating} ").grid(row=i, column=0, padx=(10, 0), pady=(10, 0))
            Label(self.playersFrame, text=name).grid(row=i, column=1, padx=(10, 0), pady=(10, 0))
            Label(self.playersFrame, text=" libre !" if free else " en  match...", fg="green" if free else "red").grid(row=i, column=2, padx=(10, 0), pady=(10, 0))
            if free == True and name != self.nickname:
                print(f"Je met un bouton à {name}")
                nickname = name
                Button(self.playersFrame, text="Défier !", command=lambda: self.askMatch(nickname)).grid(row=i, column=3, padx=(5, 0), pady=(5, 0))

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

