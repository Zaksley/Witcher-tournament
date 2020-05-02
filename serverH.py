import sys
from time import sleep, localtime
from random import randint

from PodSixNet.Server import Server
from PodSixNet.Channel import Channel

from tkinter import *

DEAD = -1
WAITING = 0
TORNAMENT = 1

class ClientChannel(Channel):
    """
    This is the server representation of a connected client.
    """
    def __init__(self, *args, **kwargs):
        Channel.__init__(self, *args, **kwargs)

        self.nickname = "anonymous"
        self.available = True
        self.rating = 1000
        self.other = None
    
    def Close(self):
        self._server.DelPlayer(self)

    def Network_newPoint(self, data):
        self.other.Send({"action": "newPoint", "coords": data["coords"], "turn": data["turn"], "who": self.nickname})

    def Network_newMove(self, data):
        self.other.Send({"action": "newMove", "coords": data["coords"], "who": self.nickname})
    
    def Network_win(self, data):
        g = self.rating
        p = self.other.rating

        self.rating = int(g + (100 - (1/3)*(g-p)))
        self.other.rating = int(p - (100 - (1/3)*(g-p)))

        self.available = True
        self.other = None

        self._server.SendPlayersList()

    def Network_lost(self, data):
        self.other.Send({"action": "win", "who": self.nickname})
        self.available = True
        self.other = None

    def Network_nickname(self, data):
        if self._server.state == TORNAMENT:
            self.Send({"action": "alreadyStarted"})
            return
        elif data["nickname"] in [p.nickname for p in self._server.players]:
            self.Send({"action": "wrongNickname"})
            return
        self.nickname = data["nickname"]

        self._server.PrintPlayers()
        self.Send({"action": "start"})

    def Network_askMatch(self, data):
        if self._server.state == WAITING:
            self.Send({"action": "tornamentNotStarted"})
            return

        nickname = data["nickname"]
        player = self._server.GetPlayer(nickname)

        if player == None:
            self.Send({"action": "matchRefused", "nickname": nickname})
            return

        delta = abs(self.rating - player.rating)
        if  delta >= 300:
            self.Send({"action": "tooHigh"})
            return

        print(f"Je suis {self.nickname} et je demande à {player.nickname} s'il veut jouer")
        player.Send({"action": "askMatch", "nickname": self.nickname, "canRefuse": delta >= 200})

    def Network_matchAccepted(self, data):
        nickname = data["nickname"]
        player = self._server.GetPlayer(nickname)

        if player == None:
            self.Send({"action": "matchRefused", "nickname": nickname})
            return

        print(f"je suis {self.nickname}, j'ai accepté un match avec {player.nickname}")

        self.other = player
        self.other.available = False
        self.other.other = self

        self.available = False

        first = randint(0, 1)
        self.launchGame(first)
        self.other.launchGame(not first)

    def Network_matchRefused(self, data):
        nickname = data["nickname"]
        player = self._server.GetPlayer(nickname)
        player.Send({"action": "matchRefused", "nickname": self.nickname})
    
    def Network_playersList(self, data):
        self._server.SendPlayersList()

    def launchGame(self, first):
        self.Send({"action" : "launchGame", "first" : first, "nickname": self.other.nickname})
    
class GameServer(Server):
    channelClass = ClientChannel
    
    def __init__(self, *args, **kwargs):
        Server.__init__(self, *args, **kwargs)
        self.players = {}
        self.state = WAITING

        self.window = Tk()
        self.window.title("Witcher Tornament - Server")
        self.window.iconphoto(False, PhotoImage(file='assets/mage_bleu_droite.png'))
        self.window.wm_minsize(320, 80)
        self.window.protocol("WM_DELETE_WINDOW", self.quit)
        self.btn = Button(self.window, text="Lancer le tournoi !", command=self.startTornament)
        self.btn.pack(expand=True, fill=BOTH)

        print('Server launched')
    
    def Connected(self, channel, addr):
        self.AddPlayer(channel)
    
    def AddPlayer(self, player):
        print("New Player connected")
        self.players[player] = True
 
    def PrintPlayers(self):
        print("players' nicknames :",[p.nickname for p in self.players])
  
    def DelPlayer(self, player):
        print("Deleting Player " + player.nickname + " at " + str(player.addr))
        del self.players[player]

        self.SendPlayersList()

    def SendToOthers(self, data):
        [p.Send(data) for p in self.players if p.nickname != data["who"]]
    
    def Broadcast(self, data):
        [p.Send(data) for p in self.players]

    def SendPlayersList(self):
        self.Broadcast({"action": "playersList", "playersList": [(p.nickname, p.available, p.rating) for p in self.players]})

    def GetPlayer(self, nickname):
        for player in self.players:
            if player.nickname == nickname:
                return player

    def startTornament(self):
        if self.state == TORNAMENT:
            return

        self.state = TORNAMENT
        self.btn.config(text="Tournoi lancé !")
        self.Broadcast({"action": "tornamentStarted"})

    def Launch(self):
        while self.state != DEAD:
            self.window.update()
            self.Pump()
            sleep(0.001)
        sys.exit()

    def quit(self):
        self.state = DEAD

# get command line argument of server, port
if len(sys.argv) != 2:
    print("Please use: python3", sys.argv[0], "host:port")
    print("e.g., python3", sys.argv[0], "localhost:31425")
else:
    host, port = sys.argv[1].split(":")
    s = GameServer(localaddr=(host, int(port)))
    s.Launch()

