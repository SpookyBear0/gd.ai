
import gd
import keyboard
import win32gui
import win32api
import win32con
import random
import time
import math
from threading import Thread
from tkinter import *
import pynput
import os

w = Tk()
mem = gd.memory.get_memory()
win = win32gui.FindWindow(None, 'Geometry Dash')
path = os.path.dirname(os.path.realpath(__file__))

def click():
    win32api.SendMessage(win, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, win32api.MAKELONG(10, 10))

def unclick():
    win32api.SendMessage(win, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, win32api.MAKELONG(10, 10))


class Brain():
    def __init__(self, framesperround):
        self.directions = []
        self.inputs = framesperround
        self.randomize()
        self.fitness = 0

    def randomize(self):
        for i in range(self.inputs):
            self.directions.append(random.uniform(0, 1) > 0.99)

    def run(self):
        mem.set_x_pos(0)
        while True:
            
            cp = mem.get_percent()
            cx = mem.get_x_pos()
            if mem.is_dead() or cp >= 100 or cx > len(self.directions):
                break
            if self.directions[math.floor(cx)]:
                click()
            else:
                unclick()
        unclick()
        self.fitness = mem.get_percent()

    def clone(self):
        clone = Brain(self.inputs)
        clone.directions = []
        for i in self.directions:
            clone.directions.append(i)

        return clone

    def mutate(self):
        mutationRate = 0.1
        for i in range(len(self.directions)):
            rand = random.uniform(0, 1)
            if rand < mutationRate:
                self.directions[i] = random.uniform(0,1) > 0.99
        
class Population:
    def __init__(self, amount, framesperround):
        self.pop = []
        for i in range(amount):
            self.pop.append(Brain(framesperround))

        self.gen = 0
        self.sumFitness = 0

    def run(self):
        self.gen += 1
        g = open(path + "/gen.txt", "w")
        g.write("Gen: " + str(self.gen))
        g.close()
        print(f'GEN {self.gen}')
        mem.player_kill()
        
        for i in range(len(self.pop)):
            s = open(path + "/species.txt", "w")
            s.write("Species: " + str(i))
            s.close()
            while mem.is_dead():
                pass
            self.pop[i].run()
            if self.pop[i].fitness >= 100:
                print(self.pop[i].directions)
                return
            print(f'FINISHED {i}/{len(self.pop)}: {self.pop[i].fitness}')
            mem.player_kill()
            
        self.naturalSelection()
        self.run()

    def naturalSelection(self):
        newPop = []

        bestDot = 0
        hiFit = 0
        for i in range(len(self.pop)):
            if self.pop[i].fitness > hiFit:
                hiFit = self.pop[i].fitness
                bestDot = i

        newPop.append(self.pop[bestDot].clone())
        for i in range(1, len(self.pop)):
            newPop.append(self.selectParent().clone())
        self.pop = newPop
        self.mutate()
    

    def getSumFitness(self):
        self.sumFitness = 0
        for brain in self.pop:
            self.sumFitness += brain.fitness

    def selectParent(self):
        runningSum = 0
        rand = random.uniform(0, self.sumFitness)

        for i in range(len(self.pop)):
            runningSum += self.pop[i].fitness
            if runningSum > rand:
                return self.pop[i]

    def mutate(self):
        for i in range(1, len(self.pop)):
            self.pop[i].mutate()
            
def update_gui():
    gentk = Label(w, text=open(path + "/gen.txt", "r").read()).grid(row=1)
    stk = Label(w, text=open(path + "/species.txt", "r").read()).grid(row=2)
    w.after(10, update_gui)
            

pop = Population(10, math.floor(mem.get_level_length() + 100))
popt = Thread(target=pop.run)
popt.start()
w.geometry()
w.after(10, update_gui)
w.mainloop()