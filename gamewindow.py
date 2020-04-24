from tkinter import *
from game import *

NB_CASE_X = 9
NB_CASE_Y = 7

WIDTH = 400
HEIGHT = 360
COLOR_P1 = "blue"
COLOR_P2 = "red"

INITIAL = 0
ACTIVE = 1

class GameWindow:
    def __init__(self, client, first):
        self.client = client
        self.first = first
        self.move = False
        self.state = ACTIVE if self.first else INITIAL
        self.cases = dict()
        self.players = [None, None]

        #SETUP GUI
        self.window = Tk()
        self.window.title("Witcher")

        self.canvas = Canvas(self.window, width=WIDTH, height=HEIGHT, bg='white')
        self.quit_btn = Button(self.window, text='Quitter', command=self.quit)

        self.canvas.bind("<Button-1>", self.playerMove)
        
        self.canvas.pack(side=TOP)
        self.quit_btn.pack(side=BOTTOM)

        #SETUP GAME
        self.drawPlateau()

    def quit(self):
        #Envoyer un signal de quitter au serveur
        self.window.destroy()

    def drawPlateau(self):
        #Draw castles
        if self.first:
            self.cases[(0, 3)] = Case(self.canvas, (0, 3), "castle")
            self.cases[(8, 3)] = Case(self.canvas, (8, 3), "ennemy_castle")
        else:
            self.cases[(8, 3)] = Case(self.canvas, (8, 3), "castle")
            self.cases[(0, 3)] = Case(self.canvas, (0, 3), "ennemy_castle")

        #Dessin de la grille
        for i in range(0, NB_CASE_X, 1):
            for j in range(0, NB_CASE_Y, 1):

                if (i,j) == (0, 3): #Castles
                    continue
                if (i,j) == (8,3):
                    continue

                if (i, j) == (4, 3): #Lake
                    continue

                self.cases[(i, j)] = Case(self.canvas, (i, j), "empty")
        
        #Draw lake and players
        self.cases[(4, 3)] = Case(self.canvas, (4, 3), "lake")
        self.players[0] = Player(self.canvas, (0, 3), 0)
        self.players[1] = Player(self.canvas, (8, 3), 1)

    def ableToMove(self):
        player = self.players[0] if self.first else self.players[1]
        (i, j) = player.coords

        for x in [-1, 0, 1]:
            for y in [-1, 0, 1]:
                #Cas du joueur
                if x == 0 and y == 0:
                    continue

                xx = i+x
                yy = j+y

                #Sort du plateau de jeu
                if xx < 0 or xx > NB_CASE_X-1 or yy < 0 or yy > NB_CASE_Y-1:
                    continue
                
                #On trouve une case disponible
                statut = self.cases[xx, yy].statut
                if statut in ["empty", "castle"]:
                    return
                    
        #Aucune case disponible
        #Maybe quitter la fenêtre
        print("Vous avez perdu !")
        self.client.Send({"action" : "lost"})

    def playerMove(self, evt):
        if self.state == ACTIVE and self.move == False:
            player = self.players[0] if self.first else self.players[1]

            for i in range(0, NB_CASE_X, 1):
                for j in range(0, NB_CASE_Y, 1):

                    x1 = XMIN+(i*DIST)-R
                    y1 = YMIN+(j*DIST)-R
                    x2 = XMIN+(i*DIST)+R
                    y2 = YMIN+(j*DIST)+R

                    #Si on clique sur une case
                    if ((evt.x < x2) and (evt.x > x1)) and ((evt.y  < y2) and (evt.y > y1)):
                        (xx, yy) = (i, j)
                        (x, y) = player.coords

                        #Tentative de se déplacer trop loin
                        if (xx>= x+2) or (xx<=x-2) or (yy>=y+2) or (yy<=y-2):
                            continue

                        #Clique sur sa propre case
                        if xx == x and yy == y:
                            continue

                        #Déplacement impossible
                        undesirable = ["occupied", "ennemy_castle", "lake"]
                        if self.cases[xx, yy].statut in undesirable:
                            continue
                        
                        #Change les statuts des cases qui doivent changer
                        forbid = ["castle", "ennemy_castle"]
                        if not self.cases[x, y].statut in forbid:
                            self.cases[x, y].statut = "empty"
                        if not self.cases[xx, yy].statut in forbid:
                            self.cases[xx, yy].statut = "occupied"

                        #Mouvement du player
                        player.move((i, j))
                        self.move = True
                        self.client.Send({"action" : "newMove", "coords" : (i,j)})

        elif self.state == ACTIVE and self.move == True:
            for i in range(0, NB_CASE_X, 1):
                for j in range(0, NB_CASE_Y, 1):

                    x1 = XMIN+(i*DIST)-R
                    y1 = YMIN+(j*DIST)-R
                    x2 = XMIN+(i*DIST)+R
                    y2 = YMIN+(j*DIST)+R

                    if ((evt.x < x2) and (evt.x > x1)) and ((evt.y  < y2) and (evt.y > y1)):          
                        if self.cases[(i,j)].statut == "empty":
                            self.cases[(i, j)].setStatut("occupied", COLOR_P1)
                            self.client.Send({"action": "newPoint", "turn" : True, "coords" : (i,j), "newStatut" : "occupied"})
                            self.state=INITIAL
                            self.move = False
                            self.ableToMove()

    def newPoint(self, data):
        (i,j) = data["coords"]
        turn = data["turn"]
        statut = data["newStatut"]

        self.cases[i, j].setStatut(statut, COLOR_P2)
        self.ableToMove()
        if turn:
            self.state = ACTIVE

    def newMove(self, data):
        (i,j) = data["coords"]

        player = self.players[1] if self.first else self.players[0]

        forbid = ["castle", "ennemy_castle"]
        if not self.cases[player.coords].statut in forbid: self.cases[player.coords].statut = "empty"
        if not self.cases[i, j].statut in forbid: self.cases[i, j].statut = "occupied"

        player.move((i, j))