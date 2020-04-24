XMIN = 40
YMIN = 80
DIST = 40
R=20

class Case():
    def __init__(self, canvas, coords, statut):
        self.canvas = canvas
        self.rock = None
        self.statut = statut
        self.coords = coords

        (i, j) = self.coords
        x1 = XMIN+(i*DIST)-R
        y1 = YMIN+(j*DIST)-R
        x2 = XMIN+(i*DIST)+R
        y2 = YMIN+(j*DIST)+R

        if self.statut == "empty":
            self.id = self.canvas.create_rectangle(x1, y1, x2, y2, fill='white')
        elif self.statut == "castle":
            self.id = self.canvas.create_rectangle(x1, y1, x2, y2, fill='blue')
        elif self.statut == "ennemy_castle":
            self.id = self.canvas.create_rectangle(x1, y1, x2, y2, fill='red')
        elif self.statut == "lake":
            self.id = self.canvas.create_rectangle(x1, y1, x2, y2, fill='aqua')
            

    def changeColor(self, newColor):
        self.canvas.itemconfig(self.id, fill = newColor)
        self.color = newColor

    def setStatut(self, statut, color):
        self.statut = statut

        if self.statut == "occupied":
			
            i, j = self.coords
            x1 = XMIN+(i*DIST)-R
            y1 = YMIN+(j*DIST)-R
            x2 = XMIN+(i*DIST)+R
            y2 = YMIN+(j*DIST)+R

            self.rock = self.canvas.create_oval(x1, y1, x2, y2, fill=color)
        

class Player():
    def __init__(self, canvas, coords, player):
        self.canvas = canvas
        self.player = player
        self.coords = coords
        
        (i, j) = self.coords
        x1 = XMIN+(i*DIST)-R
        y1 = YMIN+(j*DIST)-R
        x2 = XMIN+(i*DIST)+R
        y2 = YMIN+(j*DIST)+R

        if self.player==0:
            c = 'orange'
        else:
            c = 'pink'
    
        self.id = self.canvas.create_oval(x1, y1, x2, y2, fill=c)

    def move(self, newCoords):

        self.coords = newCoords
        (i,j) = self.coords

        x1 = XMIN+(i*DIST)-R
        y1 = YMIN+(j*DIST)-R
        x2 = XMIN+(i*DIST)+R
        y2 = YMIN+(j*DIST)+R

        self.canvas.coords(self.id, x1, y1, x2, y2)