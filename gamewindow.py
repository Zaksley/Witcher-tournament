from tkinter import *
from tkinter import messagebox
from game import *

NB_CASE_X = 9
NB_CASE_Y = 7

WIDTH = 400
HEIGHT = 360
BAND_WIDTH = 140
COLOR_P1 = "blue"
COLOR_P2 = "red"

INITIAL = 0
ACTIVE = 1
DEAD = -1
IN_GAME = 2
WAITING = 3

class GameWindow:
    def __init__(self, client, first, other):
        self.client = client
        self.other = other
        self.first = first
        self.move = False
        self.state = ACTIVE if self.first else INITIAL
        self.cases = dict()
        self.players = [None, None]

        self.colors = {"p1": COLOR_P1 if first else COLOR_P2, "p2": COLOR_P2 if first else COLOR_P1}

        #SETUP GUI
        self.window = Tk()
        self.window.iconphoto(False, PhotoImage(master=self.window, file='assets/mage_bleu_droite.png'))
        self.window.protocol("WM_DELETE_WINDOW", self.quit)
        self.window.title(f"Witcher - {client.nickname}")
        self.window.wm_minsize(width=WIDTH, height=HEIGHT+30)
        self.window.wm_maxsize(width=WIDTH, height=HEIGHT+30)

        self.canvas = Canvas(self.window, width=WIDTH, height=HEIGHT, bg='green')
        self.quit_btn = Button(self.window, text='Quitter', command=self.quit)

        self.canvas.bind("<Button-1>", self.playerMove)
        
        self.canvas.pack(side=TOP, fill=BOTH, expand=True)
        self.quit_btn.pack(side=BOTTOM)

        #SETUP GAME
        self.drawPlateau()

    def quit(self):
        if messagebox.askokcancel("Abandon", "Êtes-vous sûr de vouloir abandonner ?"):
            self.client.Send({"action" : "lost"})
            self.client.state = WAITING
            self.window.destroy()

    def drawPlateau(self):
        #Draw castles
        if self.first:
            self.cases[(0, 3)] = Case(self.canvas, (0, 3), "castle", self.first)
            self.cases[(8, 3)] = Case(self.canvas, (8, 3), "ennemy_castle", self.first)
        else:
            self.cases[(8, 3)] = Case(self.canvas, (8, 3), "castle", self.first)
            self.cases[(0, 3)] = Case(self.canvas, (0, 3), "ennemy_castle", self.first)

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


        xl = 10 + 2*XMIN
        xr = DIST + 10 + WIDTH - BAND_WIDTH


        #Draw ATH
        self.left_img = PhotoImage(master=self.canvas, file="assets/bandeau_bleu.png")
        self.left_band = self.canvas.create_image(xl, DIST, image=self.left_img)

        self.right_img = PhotoImage(master=self.canvas, file="assets/bandeau_rouge.png")
        self.right_band = self.canvas.create_image(xr, DIST, image=self.right_img)

        self.canvas.create_text(xl, DIST-7, text=self.client.nickname if self.first else self.other)
        self.canvas.create_text(xr-len(self.other)*2, DIST-7, text=self.other if self.first else self.client.nickname)

        self.state_img = PhotoImage(master=self.canvas, file=f"assets/{'etat_bouger.png' if self.first else 'etat_attendre.png'}")
        self.state_icon = self.canvas.create_image(xl + 110, DIST, image=self.state_img)

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
        self.client.Loop()
        messagebox.showinfo("Perdu", "Vous avez perdu !")
        self.window.destroy()
        self.client.state = WAITING

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

                        self.state_img = PhotoImage(master=self.canvas, file="assets/etat_pierre.png")
                        self.canvas.itemconfig(self.state_icon, image=self.state_img)

        elif self.state == ACTIVE and self.move == True:
            for i in range(0, NB_CASE_X, 1):
                for j in range(0, NB_CASE_Y, 1):

                    x1 = XMIN+(i*DIST)-R
                    y1 = YMIN+(j*DIST)-R
                    x2 = XMIN+(i*DIST)+R
                    y2 = YMIN+(j*DIST)+R

                    if ((evt.x < x2) and (evt.x > x1)) and ((evt.y  < y2) and (evt.y > y1)):          
                        if self.cases[(i,j)].statut == "empty":
                            self.cases[(i, j)].setRock(self.colors["p1"])
                            self.client.Send({"action": "newPoint", "turn" : True, "coords" : (i,j)})
                            self.state=INITIAL
                            self.move = False
                            self.state_img = PhotoImage(master=self.canvas, file="assets/etat_attendre.png")
                            self.canvas.itemconfig(self.state_icon, image=self.state_img)
                            self.ableToMove()

    def newPoint(self, data):
        (i,j) = data["coords"]
        turn = data["turn"]

        self.cases[i, j].setRock(self.colors["p2"])
        if turn:
            self.state = ACTIVE
            self.state_img = PhotoImage(master=self.canvas, file="assets/etat_bouger.png")
            self.canvas.itemconfig(self.state_icon, image=self.state_img)

        self.ableToMove()

    def newMove(self, data):
        (i,j) = data["coords"]

        player = self.players[1] if self.first else self.players[0]

        forbid = ["castle", "ennemy_castle"]
        if not self.cases[player.coords].statut in forbid: self.cases[player.coords].statut = "empty"
        if not self.cases[i, j].statut in forbid: self.cases[i, j].statut = "occupied"

        player.move((i, j))

        self.ableToMove()

if __name__ == "__main__":
    class FakeClient:
        def __init__(self):
            self.nickname = "yolo"
        def Send(self, data):
            pass

    w = GameWindow(FakeClient(), True, "yolo2")
    w.window.mainloop()