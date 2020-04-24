import sys
from time import sleep, localtime

from PodSixNet.Server import Server
from PodSixNet.Channel import Channel

class ClientChannel(Channel):
    """
    This is the server representation of a connected client.
    """
    def __init__(self, *args, **kwargs):
        Channel.__init__(self, *args, **kwargs)

        self.nickname = "anonymous"
        self.available = True
        self.other = None
    
    def Close(self):
        self._server.DelPlayer(self)

    def Network_newPoint(self, data):
        self._server.SendToOthers({"action": "newPoint", "coords": data["coords"], "newStatut": data["newStatut"], "turn": data["turn"], "who": self.nickname})

    def Network_newMove(self, data):
        self._server.SendToOthers({"action": "newMove", "coords": data["coords"], "who": self.nickname})
    
    def Network_win(self, data):
        #faire des trucs
        self.available = True
        self.other = None

    def Network_lost(self, data):
        self._server.SendToOthers({"action": "win", "who": self.nickname})
        self.available = True
        self.other = None

    def Network_nickname(self, data):
        self.nickname = data["nickname"]

        if self.nickname in self._server.players:
            self.Send({"action:": "disconnected"}) #balec juste tu peux pas te co
            return

        self._server.PrintPlayers()
        self.Send({"action": "start"})

    def Network_askMatch(self, data):
        nickname = data["nickname"]
        player = self._server.GetPlayer(nickname)
        player.Send({"action": "askMatch", "nickname": self.nickname})

    def Network_matchAccepted(self, data):
        nickname = data["nickname"]
        player = self._server.GetPlayer(nickname)

        self.other = player
        self.other.available = False
        self.available = False

        self.launchGame(False)
        self.other.launchGame(True)

    def Network_matchRefused(self, data):
        nickname = data["nickname"]
        player = self._server.GetPlayer(nickname)
        player.Send({"action": "matchRefused", "nickname": self.nickname})
    
    def Network_playersList(self, data):
        self._server.SendPlayersList()

    def launchGame(self, first):
        self.Send({"action" : "launchGame", "first" : first})
    
class MyServer(Server):
    channelClass = ClientChannel
    
    def __init__(self, *args, **kwargs):
        Server.__init__(self, *args, **kwargs)

        self.players = {}
        self.ranking = {}

        print('Server launched')
    
    def Connected(self, channel, addr):
        self.AddPlayer(channel)
    
    def AddPlayer(self, player):
        print("New Player connected")
        self.players[player] = True
 
    def PrintPlayers(self):
        print("players' nicknames :",[p.nickname for p in self.players])
  
    def DelPlayer(self, player):
        print("Deleting Player " + player.nickname + " at "+str(player.addr))
        del self.players[player]

    def SendToOthers(self, data):
        [p.Send(data) for p in self.players if p.nickname != data["who"]]
    
    def Broadcast(self, data):
        [p.Send(data) for p in self.players]

    def SendPlayersList(self):
        self.Broadcast({"action": "playersList", "playersList": [(p.nickname, p.available) for p in self.players]})

    def GetPlayer(self, nickname):
        for player in self.players:
            if player.nickname == nickname:
                return player

    def Launch(self):
        while True:
            self.Pump()
            sleep(0.001)

# get command line argument of server, port
if len(sys.argv) != 2:
    print("Please use: python3", sys.argv[0], "host:port")
    print("e.g., python3", sys.argv[0], "localhost:31425")
else:
    host, port = sys.argv[1].split(":")
    s = MyServer(localaddr=(host, int(port)))
    s.Launch()

