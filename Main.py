import random
from math import sin, pi, cos

import pyglet
from pyglet.gl import GL_TRIANGLE_FAN
from pyglet.window import key
from pyglet.window import FPSDisplay
from pyglet import clock


# Rectangle Class
class Rectangle:
    def __init__(self, x, y, width, height, Color=(26, 255, 26)):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.Color = Color
        self.Highlight = False
        self.Clicked = False
        self.HighlightColor = (0, 0, 0)
        self.NoMidlle = False
        self.draw = self.Draw

    def Draw(self):
        if self.Highlight or self.Clicked:
            if not self.Clicked:
                self.HighlightColor = (150, 150, 150)
            else:
                self.HighlightColor = (0, 0, 0)
            TextDis = [self.width, self.height, self.x, self.y]
            if self.width < 0:
                TextDis[0] *= -1
                TextDis[2] = self.x - TextDis[0]
            if self.height < 0:
                TextDis[1] *= -1
                TextDis[3] = self.y - TextDis[1]
            pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2f',
                                                         [TextDis[2] - 4, TextDis[3] - 4, TextDis[2] + TextDis[0] + 4,
                                                          TextDis[3] - 4,
                                                          TextDis[2] + TextDis[0] + 4,
                                                          TextDis[3] + TextDis[1] + 4, TextDis[2] - 4,
                                                          TextDis[3] + TextDis[1] + 4]),
                                 ('c3B', (self.HighlightColor * 4)))

        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2f',
                                                     [self.x, self.y, self.x + self.width, self.y, self.x + self.width,
                                                      self.y + self.height, self.x, self.y + self.height]),
                             ('c3B', (self.Color * 4)))

        if (self.Highlight or self.Clicked) and not self.NoMidlle:
            pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2f',
                                                         [int(self.x + self.width / 2) - 3, self.y,
                                                          int(self.x + self.width / 2) + 3, self.y,
                                                          int(self.x + self.width / 2) + 3, self.y + self.height,
                                                          int(self.x + self.width / 2) - 3, self.y + self.height]),
                                 ('c3B', (self.HighlightColor * 4)))

            pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2f',
                                                         [self.x, int(self.y + self.height / 2) - 3,
                                                          self.x, int(self.y + self.height / 2) + 3,
                                                          self.x + self.width, int(self.y + self.height / 2) + 3,
                                                          self.x + self.width, int(self.y + self.height / 2) - 3]),
                                 ('c3B', (self.HighlightColor * 4)))

class RectangleForVN:
    def __init__(self, Points, Color=(26, 255, 26)):
        self.Color = Color
        self.Points = Points

    def Draw(self):
        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2f', self.Points), ('c3B', (self.Color * 4)))

class Button(Rectangle):
    def __init__(self, x, y, width, height, color=(255, 242, 0), colorOn=(26, 255, 26),
                 mode="Lever", var=None, change=0):
        super().__init__(x, y, width, height, color)
        self.Pressed = False
        self.ColorOn = colorOn
        self.ColorOff = color
        self.Color = self.ColorOff
        if self.Pressed:
            self.Color = self.ColorOn
        self.Highlight = True
        self.NoMidlle = True
        self.Mode = mode
        self.Var = var
        self.Change = change

    def Update(self, x, y, press=True):
        if Intersects(self, x, y):
            if self.Mode == "Lever":
                self.Pressed = not self.Pressed
                if self.Pressed:
                    self.Color = self.ColorOn
                else:
                    self.Color = self.ColorOff
            elif self.Mode == "Button":
                if self.Pressed != press:
                    self.Pressed = press
                    if self.Pressed:
                        self.Var[0] += self.Change
                        self.Color = self.ColorOn
                    else:
                        self.Color = self.ColorOff
        elif self.Mode == "Button" and not press:
            self.Color = self.ColorOff
            self.Pressed = press

LowSpeedGenBTN = Button(x=750, y=370, width=20, height=20, color=(0, 255, 0), colorOn=(255, 0, 0))


CactusBatch = pyglet.graphics.Batch()
DinoBatch = pyglet.graphics.Batch()
LabelBatch = pyglet.graphics.Batch()

# Window Settings
window = pyglet.window.Window()
keys = key.KeyStateHandler()
window.push_handlers(keys)
window.set_caption("Dino Learning")
window.set_size(800, 400)
window.set_vsync(0)
pyglet.gl.glClearColor(255, 255, 255, 1)

fps_display = FPSDisplay(window)
fps_display.label.font_size = 30

CactusImg = pyglet.image.load('..\\Img\\Cactus.png')
DinoImg = pyglet.image.load_animation('..\\Img\\Dino.gif')
DinoDuckImg = pyglet.image.load_animation('..\\Img\\DinoDuck.gif')
BirdImg = pyglet.image.load_animation('..\\Img\\BirdGif.gif')

DIED = False

DinoX = 50
JumpSpd = 13
Gravity = 4
Timer = 0
Speed = 5
Dinosaurs = []
BestConnection = [[[1, 1, 1], [1, 1, 1], [1, 1, 1]],  # Input
                           [[1, 1, 1], [1, 1, 1], [1, 1, 1]],  # HL 1
                           [[1], [1]]]  # Out put

DinosLeft = 100
Gen = 0
BestFit = 0

DinosLeftLabel = pyglet.text.Label("Dinos Left - " + str(DinosLeft), x=10, y=370, italic=True, batch=LabelBatch, font_size=15, color=(0,0,0,255))
SpeedLabel = pyglet.text.Label("Speed - " + str(Speed), x=10, y=340, italic=True, batch=LabelBatch, font_size=15, color=(0,0,0,255))
GenLabel = pyglet.text.Label("Generation - " + str(Gen), x=10, y=310, italic=True, batch=LabelBatch, font_size=15, color=(0,0,0,255))
BestFitLabel = pyglet.text.Label("Best Fitness - " + str(BestFit), x=10, y=280, italic=True, batch=LabelBatch, font_size=15, color=(0,0,0,255))



def Intersects(self, x=50, y=50, Object=None, TowPoints=None):
    if Object is not None:  # Object to Object Intersect
        if ((self.x > Object.x + Object.width) or (self.x + self.width < Object.x) or
                (self.y > Object.y + Object.height) or (self.y + self.height < Object.y)):
            return False
        return True
    elif TowPoints is not None:  # Object to Imaginary Rectangle Intersect[[x,y],[x+w,y+h]]
        if ((self.x > TowPoints[1][0]) or (self.x + self.width < TowPoints[0][0]) or
                (self.y > TowPoints[1][1]) or (self.y + self.height < TowPoints[0][1])):
            return False
        return True
    else:  # Object to on point
        if self.x < x < self.x + self.width and self.y < y < self.y + self.height:
            return True
    return False


# Game classes && functions
class Dino:
    def __init__(self, Connections):
        # Draw
        self.Sprite = pyglet.sprite.Sprite(DinoImg, x=DinoX, y=55, batch=DinoBatch)
        self.Sprite.update(scale=0.5)
        # Movement
        self.Jump = False
        self.JumpInt = 0
        self.Duck = False
        self.DuckInt = 0
        # Meta
        self.Fitness = 0
        self.PrctAfterGen = 0
        self.Die = False
        self.Connections = Connections
        self.InPuts = []

    def Update(self, Spd, Dist, Y):
        self.InPuts = [Spd, Dist, Y]
        OutPuts = []
        for Output in range(len(self.Connections[-1])):
            Val = self.CalculateVal(len(self.Connections) - 1, Output)
            if Val < 0:
                Val = False
            else:
                Val = True
            OutPuts.append(Val)

        if OutPuts[0]:  # keys[key.UP]:
            self.Jump = True
        else:
            self.Jump = False
        if OutPuts[1]:  # keys[key.DOWN]
            self.Duck = True
        else:
            self.Duck = False

    def CalculateVal(self, Column, Raw):
        if Column == 0:
            return self.InPuts[Raw]  # returning raw input
        else:
            Sum = self.Connections[Column][Raw][-1]  # starting with the bias
            # adding all the values (times the weight of this specific neuron) of the previous column neurons
            for Neuron in range(len(self.Connections[Column - 1])):
                Sum += self.CalculateVal(Column - 1, Neuron) * self.Connections[Column - 1][Neuron][Raw]
            # can make an "leveler" that scale the number for -1 to 1 value
            return Sum


class Cactus:
    def __init__(self):
        self.y = 50
        self.x = random.randint(800, 1100)
        self.Sprite = pyglet.sprite.Sprite(CactusImg, x=self.x, y=self.y, batch=CactusBatch)

    def getDist(self):
        return self.Sprite.x - DinoX

    def Delete(self):
        self.Sprite.batch = None
        self.Sprite.delete()
        del self


class Bird(Cactus):
    def __init__(self):
        super().__init__()
        self.Sprite = pyglet.sprite.Sprite(BirdImg, x=self.x, y=self.y+40, batch=CactusBatch)

# Neural network classes && functions
def NextGen(Num, Random=False):
    global Timer, Speed, Objects, Dinosaurs, Gen, DinosLeft, Netpork, BestConnection
    DinosLeft = 100
    Gen += 1
    if Random:
        for i in range(Num):
            # Connections array
            Connections = [[[1, 1, 1], [1, 1, 1], [1, 1, 1]],  # Input
                           [[1, 1, 1], [1, 1, 1], [1, 1, 1]],  # HL 1
                           [[1], [1]]]  # Out put
            # Randomizing the weight of the neural network!
            for Line in Connections:
                for Object in Line:
                    for i in range(len(Object) - 1):
                        Object[i] = random.randint(-100, 100) / 100

            for j in range(len(Connections[0])):
                Connections[0][j][-1] = random.randint(-100, 100) / 100

            Dinosaurs.append(Dino(Connections))
    else:
        TotalFit = 0  # create a sum of fitnesses
        BestDinoFit = 0
        BestDinoFitNum = 0
        for Dno in Dinosaurs:  # add all of the fitnesses to the variable
            TotalFit += Dno.Fitness ** 2
            if Dno.Fitness > BestDinoFit:
                BestDinoFit = Dno.Fitness
                BestDinoFitNum = Dno.Connections
        PrctsToPicked = [0]  # create the array of the odds to be picked
        for Dno in Dinosaurs:
            Dno.PrctAfterGen = (Dno.Fitness ** 2) / TotalFit  # set the odds to be picked to every dino
            PrctsToPicked.append(Dno.PrctAfterGen + PrctsToPicked[-1])  # add it to the array (the range to be picked from)


        BestConnection = BestDinoFitNum
        Netpork.Update(BestDinoFitNum)

        PrctsToPicked[-1] = 1  # round up the last number
        PrctsToPicked.pop(0)  # remove the first variable that was used as placeholder
        RadomPears = []  # create a random pairs array
        for i in range(Num*2):  # get 200 pairs
            FLOAT = random.uniform(0, 1)
            for Plc in range(len(PrctsToPicked)):  # go through all of the odds
                if PrctsToPicked[Plc] >= FLOAT:  # check if they are within the random range
                    RadomPears.append(Plc)  # add to the pairs array
                    break
        NewDinosaurs = []
        for i in range(Num):
            NetWork1 = Dinosaurs[RadomPears[i*2+1]].Connections
            NetWork2 = Dinosaurs[RadomPears[i*2]].Connections
            NetWork = [[[None, None, None], [None, None, None], [None, None, None]],  # Input
                        [[None, None, None], [None, None, None], [None, None, None]],  # HL 1
                        [[None], [None]]]  # Output
            InFirstNetwork = True
            NeuronIndex = 0
            for Layer in range(len(NetWork)):
                for Neuron in range(len(NetWork[Layer])):
                    for Weight in range(len(NetWork[Layer][Neuron])):
                        while NetWork[Layer][Neuron][Weight] is None:
                            if NeuronIndex == 0:
                                if random.randint(1, 100) <= 80:
                                    if InFirstNetwork:
                                        NetWork[Layer][Neuron][Weight] = NetWork1[Layer][Neuron][Weight]
                                    else:
                                        NetWork[Layer][Neuron][Weight] = NetWork2[Layer][Neuron][Weight]
                                    NeuronIndex += 1
                                else:
                                    NetWork[Layer][Neuron][Weight] = random.randint(-100, 100) / 100
                                    InFirstNetwork = not InFirstNetwork
                                    NeuronIndex = 0
                            elif NeuronIndex == 1:
                                if random.randint(1, 100) <= 40:
                                    if InFirstNetwork:
                                        NetWork[Layer][Neuron][Weight] = NetWork1[Layer][Neuron][Weight]
                                    else:
                                        NetWork[Layer][Neuron][Weight] = NetWork2[Layer][Neuron][Weight]
                                    NeuronIndex += 1
                                else:
                                    InFirstNetwork = not InFirstNetwork
                                    NeuronIndex = 0
                            elif NeuronIndex == 2:
                                if random.randint(1, 100) <= 20:
                                    if InFirstNetwork:
                                        NetWork[Layer][Neuron][Weight] = NetWork1[Layer][Neuron][Weight]
                                    else:
                                        NetWork[Layer][Neuron][Weight] = NetWork2[Layer][Neuron][Weight]
                                InFirstNetwork = not InFirstNetwork
                                NeuronIndex = 0
            for Line in range(len(NetWork)-1):
                for Neuron in range(len(NetWork[Line+1])):
                    NetWork[Line+1][Neuron][-1] = 1
            #for Net in [NetWork1, NetWork2, NetWork]:
            #    for Line in Net:
            #        print(Line)
            NewDinosaurs.append(Dino(NetWork))

        # Reset Veriables
        Timer = 0
        Speed = 5
        Dinosaurs = [i for i in NewDinosaurs]
        for Obj in Objects:
            Obj.Delete()
        Objects = [Cactus()]

class Circle:
    def __init__(self, x, y, radius, color=(153, 50, 204)):
        iterations = int(2 * radius * pi)
        s = sin(2 * pi / iterations)
        c = cos(2 * pi / iterations)
        dx, dy = radius, 0

        self.Points = [x, y]
        self.color = color
        self.x = x
        self.y = y

        for i in range(iterations + 1):
            self.Points.append(x + dx)
            self.Points.append(y + dy)
            dx, dy = (dx * c - dy * s), (dy * c + dx * s)

    def Draw(self):
        pyglet.graphics.draw(int(len(self.Points) / 2), GL_TRIANGLE_FAN, ('v2f', self.Points),
                             ('c3B', (self.color * int(len(self.Points) / 2))))

    def __del__(self):
        del self

class VisualNetwork:
    def __init__(self, x, y, Connections, color=(0,0,0)):
        self.Weights = [[[None for W in N[:-1]]for N in L] for L in Connections]
        self.Weights[0] = [[None for W in N]for N in Connections[0]]
        for i in self.Weights:
            print(i)
        self.Neurons = [[None for N in L] for L in Connections]

        for Layer in range(len(Connections)):
            for Neuron in range(len(Connections[Layer])):
                self.Neurons[Layer][Neuron] = Circle(x+((Layer+1)*70), y+((Neuron+1)*50)-len(Connections[Layer])*25, 10, color=color)
        for Layer in range(len(self.Weights)):
            for Neuron in range(len(self.Weights[Layer])):
                N = self.Neurons[Layer][Neuron]
                for Weight in range(len(self.Weights[Layer][Neuron])):
                    N2 = self.Neurons[Layer+1][Weight]
                    if Connections[Layer][Neuron][Weight] > 0:
                        self.Weights[Layer][Neuron][Weight] = RectangleForVN([N.x, N.y-5, N.x, N.y+5, N2.x, N2.y-5, N2.x, N2.y+5],
                                                                         Color=(0, int(abs(Connections[Layer][Neuron][Weight]*255)), 0))
                    else:
                        self.Weights[Layer][Neuron][Weight] = RectangleForVN(
                            [N.x, N.y - 5, N.x, N.y + 5, N2.x, N2.y - 5, N2.x, N2.y + 5],
                            Color=(int(abs(Connections[Layer][Neuron][Weight] * 255)),0, 0))

    def Draw(self):
        for Layer in self.Weights:
            for Neuron in Layer:
                for Weight in Neuron:
                    Weight.Draw()

        for Layer in self.Neurons:
            for Neuron in Layer:
                Neuron.Draw()

    def Update(self, Connections):
        for Layer in range(len(self.Weights)):
            for Neuron in range(len(self.Weights[Layer])):
                for Weight in range(len(self.Weights[Layer][Neuron])):
                    if Connections[Layer][Neuron][Weight] > 0:
                        self.Weights[Layer][Neuron][Weight].Color = (0, int(abs(Connections[Layer][Neuron][Weight] * 255)), 0)
                    else:
                        self.Weights[Layer][Neuron][Weight].Color = (int(abs(Connections[Layer][Neuron][Weight] * 255)), 0, 0)



# Last Minute
Line = Rectangle(0, 50, 800, 5, Color=(0, 0, 0))
Objects = [Cactus()]

Netpork = VisualNetwork(250, 300, BestConnection)

@window.event
def on_mouse_press(x, y, button, modifiers):
    LowSpeedGenBTN.Update(x, y)
    pass


@window.event
def on_draw():
    window.clear()
    Line.Draw()
    CactusBatch.draw()
    DinoBatch.draw()
    LabelBatch.draw()
    fps_display.draw()
    LowSpeedGenBTN.draw()
    if not LowSpeedGenBTN.Pressed:
        Netpork.Draw()


@window.event
def update(dt):
    global Objects, Timer, Dinosaurs, Speed, DinosLeft, Gen, DinosLeftLabel, SpeedLabel, GenLabel, BestFit, BestFitLabel
    global DIED
    dt = clock.tick()

    if LowSpeedGenBTN.Pressed:
        clock.set_fps_limit(1000)
    else:
        clock.set_fps_limit(60)


    # Checking the for closes object
    DistFromObj = 2000
    ObjHeight = 0
    for i in range(len(Objects)):
        if 0 <= Objects[i].getDist():
            DistFromObj = Objects[i].getDist()
            if Objects[i].__class__.__name__ == "Bird":
                ObjHeight = 1
            break
    DistFromObj /= 1000

    # Update Objects and Check for Dino-Object interaction
    Countine = False
    for Obj in Objects:
            Obj.Sprite.x -= Speed
            if Obj.Sprite.x <= -Obj.Sprite.width:
                Objects.remove(Obj)
                Obj.Delete()
                break
            DnoALive = len(Dinosaurs)
            for Dno in Dinosaurs:
                if not Dno.Die:
                    if Intersects(Dno.Sprite, Object=Obj.Sprite):
                        Dno.Sprite.batch = None
                        Dno.Die = True
                        DinosLeft -= 1
                else:
                    DnoALive -= 1

            if DnoALive == 0:  # if the gen is over
                if Speed > BestFit:
                    BestFit = Speed
                NextGen(len(Dinosaurs))
                DIED = True
                Countine = True
                break

    # Stopping the program if all the dinos are dead
    if not Countine:
        # Draw a new Object
        Timer += 1
        if Timer >= 200:
            if random.randint(0, 1) == 0:
                Objects.append(Cactus())
            else:
                Objects.append(Bird())
            Speed += 0.1
            Timer = 0

        # Update Dinosaurs
        for Dno in Dinosaurs:
            if not Dno.Die:
                Dno.Fitness += 1
                Dno.Update(Speed/20, DistFromObj, ObjHeight)
                # Jump: 0 - No jumping, 1 - Going up, 2 - going down
                if not Dno.JumpInt == 0:
                    if Dno.DuckInt == 1:
                        Dno.Sprite.image = DinoImg
                        Dno.DuckInt = 0
                    if Dno.JumpInt == 1:
                        Dno.Sprite.y += JumpSpd
                        if Dno.Sprite.y >= 200:
                            Dno.JumpInt = 2
                            Dno.Sprite.y = 200
                    else:
                        Dno.Sprite.y -= Gravity
                        if Dno.Sprite.y <= 55:
                            Dno.JumpInt = 0
                            Dno.Sprite.y = 55
                elif Dno.Jump:
                    Dno.JumpInt = 1
                elif Dno.Duck:
                    if Dno.DuckInt == 0:
                        Dno.Sprite.image = DinoDuckImg
                        Dno.DuckInt = 1
                else:
                    if Dno.DuckInt == 1:
                        Dno.Sprite.image = DinoImg
                        Dno.DuckInt = 0

    # Label update
    DinosLeftLabel.text = "Dinos Left - " + str(DinosLeft)
    SpeedLabel.text = "Speed/Fitness - " + str(int((Speed*10)-50))
    GenLabel.text = "Generation - " + str(Gen)
    if DIED:
        BestFitLabel.text = "Best Fitness - " + str(int((BestFit*10)-50))

# Stating The Program
if __name__ == "__main__":
    # Starting the main loop
    NextGen(100, True)
    pyglet.clock.schedule_interval(update, 1 / 1000)  # Loop speed
    pyglet.app.run()
