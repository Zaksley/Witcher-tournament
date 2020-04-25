import random
from tkinter import PhotoImage

XMIN = 40
YMIN = 80
DIST = 40
R = 20

class Case():
    def __init__(self, canvas, coords, statut):
        self.canvas = canvas
        self.rock = None
        self.rock_img = None
        self.statut = statut
        self.coords = coords
        self.img = None

        (i, j) = self.coords
        x1 = XMIN+(i*DIST)
        y1 = YMIN+(j*DIST)


        if self.statut == "empty":
            c1 = (0, 0.15)
            c2 = (0.15, 0.85)
            c3 = (0.85, 1)
            r = random.random()
            i = 0

            if c1[0] <= r < c1[1]: i = 2
            elif c2[0] <= r < c2[1]: i = 1
            elif c3[0] <= r <= c3[1]: i = 3        

            self.img = PhotoImage(master=self.canvas, file=f"assets/case{i}.png")
        elif self.statut == "castle":
            self.img = PhotoImage(master=self.canvas, file="assets/chateau_bleu.png")
        elif self.statut == "ennemy_castle":
            self.img = PhotoImage(master=self.canvas, file="assets/chateau_rouge.png")
        elif self.statut == "lake":
            self.img = PhotoImage(master=self.canvas, file="assets/lac.png")
        
        self.id = self.canvas.create_image(x1, y1, image=self.img)
            

    def changeColor(self, newColor):
        self.canvas.itemconfig(self.id, fill = newColor)
        self.color = newColor

    def setRock(self, color):
        self.statut = "occupied"

        i, j = self.coords
        x1 = XMIN+(i*DIST)
        y1 = YMIN+(j*DIST)

        self.rock_img = PhotoImage(master=self.canvas, file=f"assets/{color}_rock.png")
        self.rock = self.canvas.create_image(x1, y1, image=self.rock_img)
        

class Player():
    def __init__(self, canvas, coords, player):
        self.canvas = canvas
        self.player = player
        self.coords = coords
        self.img = None
        
        (i, j) = self.coords
        x1 = XMIN+(i*DIST)
        y1 = YMIN+(j*DIST)

        if self.player == 0:
            self.img = PhotoImage(master=self.canvas, file="assets/mage_bleu_droite.png")
        else:
            self.img = PhotoImage(master=self.canvas, file="assets/mage_rouge_gauche.png")
    
        self.id = self.canvas.create_image(x1, y1, image=self.img)

    def move(self, newCoords):
        self.coords = newCoords
        (i,j) = self.coords
        x1 = XMIN+(i*DIST)
        y1 = YMIN+(j*DIST)

        self.canvas.coords(self.id, x1, y1)