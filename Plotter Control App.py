from multiprocessing.managers import SharedMemoryManager
import tkinter as tk
import time
from paho.mqtt import client as mqtt_client
from multiprocessing import Process
from multiprocessing.shared_memory import ShareableList
from multiprocessing.shared_memory import SharedMemory
from threading import Thread
from math import cos,atan2,acos,sin,sqrt,pi,sin
import psycopg
import torch
import threading
from diffusers import StableDiffusionPipeline
from PIL import Image, ImageTk, ImageOps
from datetime import datetime
import numpy as np
import cv2
import json
from scipy.spatial import distance
from PIL import ImageDraw 
import math
import time
from tkinter import ttk
con = psycopg.connect(
   dbname="robot_new",
   user="postgres",
   password="Kacpry",
   host="localhost",
   port= '5432'
   )

def DegToRad(deg):
    return deg*pi/180
def draw_circle(s1,s2,shm_name):
    if(s2[15]):
        s2[27] = 'KOLO'

def draw_iks(s1,s2,shm_name):
    if(s2[15]):
        s2[27] = 'iks'

def draw_square(s1,s2,shm_name):
    if(s2[15]):
        s2[27] = 'kwadrat'
def insertToDatabase(self,shm_name):
    s2 = ShareableList(name=shm_name)
    if s2[30] == 1:
        s2[29] = 1
        punkty = []
        with open('punkty.txt', 'r') as plik:
            prompt = plik.readline()
            for linia in plik:
                if ',' in linia:
                    x_str, y_str = linia.strip().split(',')
                    try:
                        x = float(x_str.strip())
                        y = float(y_str.strip())
                        # Odwrócenie punktu o 180 stopni wokół środka (0,0)
                        punkty.append((x, y))
                    except ValueError:
                        print(f"Nieprawidłowy wiersz: {linia.strip()}")

        curs_obj = con.cursor()
        curs_obj.execute("SELECT COUNT (id_rysunku) FROM Rysunki")
        row1 = curs_obj.fetchone()
        row2 = int(row1[0])
        numberrys = row2 - 1
        current_time = datetime.now()
        data = current_time.date()
        curs_obj.execute("INSERT INTO Rysunki(id_rysunku,rozp_generacji,kon_generacji,date,prompt) VALUES(%s,%s,%s,%s,%s);",(numberrys,s2[32],s2[33],data,prompt))
        con.commit()
        print('DATA INSERTED Rysunki')
        x_temp = []
        y_temp = []
        for i in range(4,len(punkty)):
            x, y = punkty[i]
            x_temp.append(x)
            y_temp.append(y)
            if i < len(punkty) - 1:
                x2, y2 = punkty[i + 1]
                dystans = math.hypot(x2 - x, y2 - y)
                if dystans > 12:
                    s2[19] = 0
                else:
                    s2[19] = 1
                x_temp = []
                y_temp = []
            calculateKinematics(x,y,shm_name=shm_name,tryb='RECZNY')
            curs_obj = con.cursor()
            curs_obj.execute("SELECT COUNT (id_pozycji) FROM Pozycje")
            row1 = curs_obj.fetchone()
            row2 = int(row1[0])
            numberpoz = row2 - 1
            current_time = datetime.now()
            timestamp = current_time.strftime("%H:%M:%S") 
            data = current_time.date()
            curs_obj.execute("INSERT INTO Pozycje(id_pozycji,x,y,timestamp,date,id_rysunku) VALUES(%s,%s,%s,%s,%s,%s);",(numberpoz,x,y,timestamp,data,numberrys))
            con.commit()
            print('DATA INSERTED Pozycje')
            curs_obj = con.cursor()
            curs_obj.execute("SELECT COUNT (id_katow) FROM Katy")
            row1 = curs_obj.fetchone()
            row2 = int(row1[0])
            number = row2 - 1
            curs_obj.execute("INSERT INTO Katy(id_katow,th1,th2,czy_opuszczony,id_pozycji) VALUES(%s,%s,%s,%s,%s);",(number,s2[13],s2[14],s2[19],numberpoz))
            con.commit()
            print('DATA INSERTED Katy')
        s2[31] = 1

def reczny_button(s1,s2,shm_name):
    global mem1
    s2 = ShareableList(name=shm_name)
    mem1 = SharedMemoryManager()
    if ((s2[15] == 0 or s2[15] == None) and s2[29] != 1):
        s2[15] = 1
        if (s2[26] == 0 or s2[26] == None):
            s2[26] = 1
        for i in range(9):
            s1[i] = ""
        s2[28] = "AUTO"
    elif((s2[15] == 1) and s2[29] != 1):
        s2[15] = 0
        s2[16] = 1
        s2[28] = "MAN"
def z_button(s1,s2,shm_name):
    if (s2[19] == 0 or s2[19] == None) and s2[15] == 1 and s2[29] != 1:
        s2[19] = 1
        s2[20] = 'Podnies'
        s2[21] = 'Podnies'
    elif(s2[19] == 1 and s2[15] == 1) and s2[29] != 1:
        s2[19] = 0   
        s2[20] = 'Opuść'
        s2[21] = 'Opuść'
def rozmiesc(start, stop, num):
    if num < 2:
        return [start]
    step = (stop - start) / (num - 1)
    return [start + i * step for i in range(num)]
def sendToRobot(self,shm_name):
    s2 = ShareableList(name=shm_name)
    wiad = {"th1": s2[13],"th2": s2[14], "z" : s2[19]}
    wys = json.dumps(wiad)
    self.client.publish('reczny',wys,qos=0)
    print("WYSLALANO Katy")
    print(f"Katy: {wiad}")  
def savePozAng(x,y,shm_name):
    s2 = ShareableList(name=shm_name)
    curs_obj = con.cursor()
    curs_obj.execute("SELECT COUNT (id_pozycji) FROM Pozycje")
    row1 = curs_obj.fetchone()
    row2 = int(row1[0])
    numberpoz = row2 - 1
    current_time = datetime.now()
    timestamp = current_time.strftime("%H:%M:%S") 
    data = current_time.date()
    curs_obj.execute("INSERT INTO Pozycje(id_pozycji,x,y,timestamp,date) VALUES(%s,%s,%s,%s,%s);",(numberpoz,x,y,timestamp,data))
    con.commit()
    print('DATA INSERTED Pozycje')
    curs_obj = con.cursor()
    curs_obj.execute("SELECT COUNT (id_katow) FROM Katy")
    row1 = curs_obj.fetchone()
    row2 = int(row1[0])
    number = row2 - 1
    curs_obj.execute("INSERT INTO Katy(id_katow,th1,th2,czy_opuszczony,id_pozycji) VALUES(%s,%s,%s,%s,%s);",(number,s2[13],s2[14],s2[19],numberpoz))
    con.commit()
    print('DATA INSERTED Katy')
class MyMQTT1:
    def __init__(self,broker,port,topic,client_id, s1,shm_name):
        self.broker = broker
        self.topic = topic
        self.port = port
        self.client_id = client_id
        self.shm_name = shm_name
        self.client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2,client_id, True)
        self.client.on_connect = self.on_connect
    def on_connect(self, client, userdata, flags, rc, props=None):
        if rc == 0:
            print("Connected to MQTT Broker!")
            self.client.subscribe(self.topic,qos=0)
        else:
            print("Failed to connect, return code %d\n", rc)
            self.client.subscribe(self.topic,qos=0)
            #Metoda do łączenia z brokerem
    def connect(self):
        self.client.connect(self.broker, self.port, 300)
    # Metoda do publikowania wiadomości
    def publish(self, message):
        self.client.publish(self.topic, message, qos= 0)
        print(f"Wysłano wiadomość: {message}")
    # Uruchomienie głównej pętli klienta MQTT
    def start(self):
        self.client.loop_start()
    # Zatrzymanie klienta
    def stop(self):
        self.client.loop_stop()
    def loop_d(self,shm_name,s1):
        s2 = ShareableList(name=shm_name)
        self.connect()
        self.start()
        if s2[11] == None and s2[12] == None:
            s2[11] = 0
            s2[12] = 0
        lastx = 0
        lasty = 0
        odstep = 0.1
        while True:
            time.sleep(0.1)
            if s2[26] == 1:
                lastx = 0
                lasty = 0
                s2[26] = 0
            s2[11] = lastx
            s2[12] = lasty
            if s2[31]:
                punkty = []
                x_temp = []
                y_temp = []
                with open('punkty.txt', 'r') as plik:
                    for linia in plik:
                        if ',' in linia:
                            x_str, y_str = linia.strip().split(',')
                            try:
                                x = float(x_str.strip())
                                y = float(y_str.strip())
                                # Odwrócenie punktu o 180 stopni wokół środka (0,0)
                                punkty.append((x, y))
                            except ValueError:
                                print(f"Nieprawidłowy wiersz: {linia.strip()}")
                s2[19] = 0
                for i in range(4,len(punkty)):
                    x, y = punkty[i]
                    x_temp.append(x)
                    y_temp.append(y)
                    if i < len(punkty) - 1:
                        x2, y2 = punkty[i + 1]
                        dystans = math.hypot(x2 - x, y2 - y)
                        if dystans > 12:
                            s2[19] = 0
                        else:
                            s2[19] = 1
                        x_temp = []
                        y_temp = []
                    time.sleep(0.15)
                    calculateKinematics(x,y,shm_name=shm_name,tryb='RECZNY')
                    sendToRobot(self,shm_name=shm_name)
                s2[29] = 0
                s2[30] = 0
                s2[31] = 0
                s2[19] = 0
                calculateKinematics(0,0,shm_name=shm_name,tryb='RECZNY')
                sendToRobot(self,shm_name=shm_name)
            if s2[27] == 'KOLO':
                r = 20
                j = 0
                xtemp = s2[11]
                ytemp = s2[12]
                s2[19] = 0
                calculateKinematics(xtemp,ytemp,shm_name,'RECZNY')
                sendToRobot(self, shm_name=shm_name)
                time.sleep(0.2)
                s2[19] = 1
                theta = rozmiesc(0, 2*pi + 0.3, 100)
                for i in theta:
                    j = j+1
                    time.sleep(odstep)
                    x = xtemp + r*cos(i)
                    y = ytemp + r*sin(i)
                    calculateKinematics(x,y,shm_name,'RECZNY')
                    sendToRobot(self, shm_name=shm_name)
                    if j%10 == 0:
                        savePozAng(x,y,shm_name)
                s2[19] = 0
                calculateKinematics(xtemp + r*cos(2*pi),ytemp + r*sin(2*pi),shm_name,'RECZNY')
                sendToRobot(self, shm_name=shm_name)
                time.sleep(1)
                s2[11] = xtemp
                s2[12] = ytemp
                s2[27] = ""
                calculateKinematics(s2[11],s2[12],shm_name,'RECZNY')
                sendToRobot(self, shm_name=shm_name)
            if s2[27] == 'iks':
                r = 20
                xtemp = s2[11]
                ytemp = s2[12]
                s2[19] = 0
                calculateKinematics(xtemp,ytemp,shm_name,'RECZNY')
                sendToRobot(self, shm_name=shm_name)
                x1 = r + xtemp
                y1 = r + ytemp
                j = 0
                time.sleep(0.2)
                s2[19] = 1
                move1 = rozmiesc(0, 2*r, 40)
                for i in move1:
                    j=j+1
                    time.sleep(odstep)
                    x = x1 - i
                    y = y1 - i
                    s2[11] = x
                    s2[12] = y
                    calculateKinematics(x,y,shm_name,'RECZNY')
                    sendToRobot(self, shm_name=shm_name)
                    if j%10 == 0:
                        savePozAng(x,y,shm_name)
                s2[19] = 0
                calculateKinematics(s2[11],s2[12],shm_name,'RECZNY')
                sendToRobot(self, shm_name=shm_name)
                s2[11] = x
                s2[12] = y1
                xtemp1 = s2[11]
                ytemp1 = s2[12]
                time.sleep(1)
                s2[19] = 1
                j=0
                move2 = rozmiesc(0, 2*r, 40)
                for i in move2:
                    j=j+1
                    time.sleep(odstep)
                    x = xtemp1 + i
                    y = ytemp1 - i
                    s2[11] = x
                    s2[12] = y
                    calculateKinematics(x,y,shm_name,'RECZNY')
                    sendToRobot(self, shm_name=shm_name)
                    if j%10 == 0:
                        savePozAng(x,y,shm_name)
                s2[19] = 0
                calculateKinematics(s2[11],s2[12],shm_name,'RECZNY')
                sendToRobot(self, shm_name=shm_name)
                time.sleep(1.5)
                s2[11] = xtemp
                s2[12] = ytemp
                calculateKinematics(s2[11],s2[12],shm_name,'RECZNY')
                sendToRobot(self, shm_name=shm_name)
                s2[27] = ""
            if s2[27] == 'kwadrat':
                r = 40
                s2[19] = 0
                j=0
                calculateKinematics(s2[11],s2[12],shm_name,'RECZNY')
                sendToRobot(self, shm_name=shm_name)
                xtemp1 = s2[11]
                ytemp1 = s2[12]
                xtemp = xtemp1 + r/2
                ytemp = ytemp1 + r/2
                time.sleep(0.5)
                calculateKinematics(xtemp,ytemp,shm_name,'RECZNY')
                sendToRobot(self, shm_name=shm_name)
                time.sleep(0.6)
                s2[19] = 1
                move = rozmiesc(0, r, 40)
                for i in move:
                    time.sleep(odstep)
                    x = xtemp - i
                    y = ytemp
                    calculateKinematics(x,y,shm_name,'RECZNY')
                    sendToRobot(self, shm_name=shm_name)
                    if j%10 == 0:
                        savePozAng(x,y,shm_name)
                xtemp = x
                ytemp = y 
                j=0
                for i in move:
                    time.sleep(odstep)
                    x = xtemp
                    y = ytemp - i
                    calculateKinematics(x,y,shm_name,'RECZNY')
                    sendToRobot(self, shm_name=shm_name)
                    if j%10 == 0:
                        savePozAng(x,y,shm_name)
                xtemp = x
                ytemp = y 
                j=0
                for i in move:
                    time.sleep(odstep)
                    x = xtemp + i
                    y = ytemp
                    calculateKinematics(x,y,shm_name,'RECZNY')
                    sendToRobot(self, shm_name=shm_name)
                    if j%10 == 0:
                        savePozAng(x,y,shm_name)
                xtemp = x
                ytemp = y 
                j=0
                move = rozmiesc(0, r+2, 40)
                for i in move:
                    time.sleep(odstep)
                    x = xtemp
                    y = ytemp + i
                    calculateKinematics(x,y,shm_name,'RECZNY')
                    sendToRobot(self, shm_name=shm_name)
                    if j%10 == 0:
                        savePozAng(x,y,shm_name)
                xtemp = x
                ytemp = y
                s2[19] = 0
                calculateKinematics(xtemp,ytemp,shm_name,'RECZNY')
                sendToRobot(self, shm_name=shm_name)
                time.sleep(1)
                s2[19] = 0
                s2[11] = xtemp1
                s2[12] = ytemp1
                calculateKinematics(s2[11],s2[12],shm_name,'RECZNY')
                sendToRobot(self, shm_name=shm_name)
                s2[27] = ""
            if s2[27] == '':
                if s2[9] == 'L':
                    s2[12] += float(s2[22])
                if s2[9] == 'P':
                    s2[12] -= float(s2[22]) 
                if s2[9] == 'D':
                    s2[11] -= float(s2[22])
                if s2[9] == 'G':
                    s2[11] += float(s2[22])
                if s2[9] == 'GL':
                    s2[11] += float(s2[22])
                    s2[12] += float(s2[22])
                if s2[9] == 'DL':
                    s2[12] += float(s2[22])
                    s2[11] -= float(s2[22])
                if s2[9] == 'DP':
                    s2[11] -= float(s2[22])
                    s2[12] -= float(s2[22])
                if s2[9] == 'GP':
                    s2[11] += float(s2[22])
                    s2[12] -= float(s2[22])  
                if s2[9] == 'HOME':
                    s2[11] = 0
                    s2[12] = 0
                if s2[17] == 1 and s2[9] != '' or s2[20] != '':
                    curs_obj = con.cursor()
                    curs_obj.execute("SELECT COUNT (id_pozycji) FROM Pozycje")
                    row1 = curs_obj.fetchone()
                    row2 = int(row1[0])
                    numberpoz = row2 - 1
                    current_time = datetime.now()
                    timestamp = current_time.strftime("%H:%M:%S") 
                    data = current_time.date()
                    print()
                    curs_obj.execute("INSERT INTO Pozycje(id_pozycji,x,y,timestamp,date) VALUES(%s,%s,%s,%s,%s);",(numberpoz,s2[11],s2[12],timestamp,data))
                    con.commit()
                    print('DATA INSERTED Pozycje')
                    if s2[22] == "1":
                        calculateKinematics(s2[11],s2[12],self.shm_name,'RECZNY')
                        wiad = {"th1": s2[13],"th2": s2[14], "z" : s2[19]}
                        curs_obj = con.cursor()
                        curs_obj.execute("SELECT COUNT (id_katow) FROM Katy")
                        row1 = curs_obj.fetchone()
                        row2 = int(row1[0])
                        number = row2 - 1
                        curs_obj.execute("INSERT INTO Katy(id_katow,th1,th2,czy_opuszczony,id_pozycji) VALUES(%s,%s,%s,%s,%s);",(number,s2[13],s2[14],s2[19],numberpoz))
                        con.commit()
                        print('DATA INSERTED Katy')
                        wys = json.dumps(wiad)
                        self.client.publish('reczny',wys,qos=0)
                        print("WYSLALANO Katy")
                        print(f"Katy: {wiad}")   
                    elif s2[22] == "10":
                        tempx = np.linspace(lastx,s2[11],50)
                        tempy = np.linspace(lasty,s2[12],50)
                        for i in range(50):
                            calculateKinematics(tempx[i],tempy[i],self.shm_name,'RECZNY')
                            wiad = {"th1": s2[13],"th2": s2[14], "z" : s2[19]}
                            curs_obj = con.cursor()
                            curs_obj.execute("SELECT COUNT (id_katow) FROM Katy")
                            row1 = curs_obj.fetchone()
                            row2 = int(row1[0])
                            number = row2 - 1
                            curs_obj.execute("INSERT INTO Katy(id_katow,th1,th2,czy_opuszczony,id_pozycji) VALUES(%s,%s,%s,%s,%s);",(number,s2[13],s2[14],s2[19],numberpoz))
                            con.commit()
                            print('DATA INSERTED Katy')
                            wys = json.dumps(wiad)
                            self.client.publish('reczny',wys,qos=0)
                            print("WYSLALANO Katy")
                            print(f"Katy: {wiad}")   
                            time.sleep(0.01)
                    elif s2[22] == "50":
                        tempx = np.linspace(lastx,s2[11],200)
                        tempy = np.linspace(lasty,s2[12],200)
                        for i in range(200):
                            calculateKinematics(tempx[i],tempy[i],self.shm_name,'RECZNY')
                            wiad = {"th1": s2[13],"th2": s2[14], "z" : s2[19]}
                            curs_obj = con.cursor()
                            curs_obj.execute("SELECT COUNT (id_katow) FROM Katy")
                            row1 = curs_obj.fetchone()
                            row2 = int(row1[0])
                            number = row2 - 1
                            curs_obj.execute("INSERT INTO Katy(id_katow,th1,th2,czy_opuszczony,id_pozycji) VALUES(%s,%s,%s,%s,%s);",(number,s2[13],s2[14],s2[19],numberpoz))
                            con.commit()
                            print('DATA INSERTED Katy')
                            wys = json.dumps(wiad)
                            self.client.publish('reczny',wys,qos=0)
                            print("WYSLALANO Katy")
                            print(f"Katy: {wiad}")                        
                            time.sleep(0.01)
            lastx = s2[11]
            lasty = s2[12]
            s2[9] = ''
            s2[20] = ''
            if s2[15] == 1 and (s2[17] == 0 or s2[17] == None):
                s2[17] = 1
            if s2[16] == 1:
                s2[17] = 0
                s2[16] = 0
def create_dpad(canvas, center_x, center_y, size, callback, shm_name):
    arrow_length = size * 1.5
    gap = size // 2  # Dystans między przyciskiem HOME a strzałkami
    half_size = size // 2

    # Funkcja pomocnicza do rysowania strzałek
    def draw_arrow(points, color, name):
        polygon = canvas.create_polygon(points, fill=color, outline="black")
        canvas.tag_bind(polygon, "<Button-1>", lambda e: callback(shm_name,name))

    # Górna strzałka
    draw_arrow([
        center_x, center_y - (arrow_length + gap),
        center_x - half_size, center_y - gap - half_size,
        center_x + half_size, center_y - gap - half_size
    ], "gray", "G")

    # Dolna strzałka
    draw_arrow([
        center_x, center_y + (arrow_length + gap), 
        center_x - half_size, center_y + gap + half_size,
        center_x + half_size, center_y + gap + half_size
    ], "gray", "D")

    # Lewa strzałka
    draw_arrow([
        center_x - (arrow_length + gap), center_y,
        center_x - gap - half_size, center_y - half_size,
        center_x - gap - half_size, center_y + half_size
    ], "gray", "L")

    # Prawa strzałka
    draw_arrow([
        center_x + (arrow_length + gap), center_y,
        center_x + gap + half_size, center_y - half_size,
        center_x + gap + half_size, center_y + half_size
    ], "gray", "P")

    # Górno-lewa strzałka
    draw_arrow([
        center_x - (arrow_length + gap), center_y - (arrow_length + gap),
        center_x - gap - half_size, center_y - (arrow_length + gap),
        center_x - (arrow_length + gap), center_y - gap - half_size
    ], "lightgray", "GL")

    # Górno-prawa strzałka
    draw_arrow([
        center_x + (arrow_length + gap), center_y - (arrow_length + gap),
        center_x + gap + half_size, center_y - (arrow_length + gap),
        center_x + (arrow_length + gap), center_y - gap - half_size
    ], "lightgray", "GP")

    # Dolno-lewa strzałka
    draw_arrow([
        center_x - (arrow_length + gap), center_y + (arrow_length + gap),
        center_x - gap - half_size, center_y + (arrow_length + gap),
        center_x - (arrow_length + gap), center_y + gap + half_size
    ], "lightgray", "DL")

    # Dolno-prawa strzałka
    draw_arrow([
        center_x + (arrow_length + gap), center_y + (arrow_length + gap),
        center_x + gap + half_size, center_y + (arrow_length + gap), 
        center_x + (arrow_length + gap), center_y + gap + half_size
    ], "lightgray", "DP")

    # Przycisk HOME
    home_button = canvas.create_oval(
        center_x - (half_size + 5), center_y - (half_size + 5),
        center_x + (half_size + 5), center_y + (half_size + 5),
        fill="white", outline="black"
    )
    home_hitbox = canvas.create_oval(
        center_x - (half_size + 5), center_y - (half_size + 5),
        center_x + (half_size + 5), center_y + (half_size + 5),
        fill="", outline=""
)
    canvas.create_text(center_x, center_y, text="HOME", font=("Arial", 10, "bold"))
    canvas.tag_bind(home_button, "<Button-1>", lambda e: callback(shm_name,"HOME"))
    canvas.tag_bind(home_hitbox, "<Button-1>", lambda e: callback(shm_name,"HOME"))
def on_radio_click(button,shm_name):
    s2 = ShareableList(name=shm_name)
    s2[22] = button.cget("text")
    s2[23] = s2[24] = s2[25] = "normal"
    if s2[22] == "1":
        s2[23] = "disabled"
    if s2[22] == "10":
        s2[24] = "disabled"
    if s2[22] == "50":
        s2[25] = "disabled"
# Funkcja obsługująca kliknięcia
def on_click(shm_name,name):
    s2 = ShareableList(name=shm_name)
    s2[9] = name
def draw_points_on_image(points, image_pil, point_color=(0, 0, 0), point_size=1):
    if image_pil is None:
        return Image.new('RGB', (512, 512), color='white')

    width, height = image_pil.size

    if points is None or len(points) == 0:
        return Image.new('RGB', (width, height), color='white')

    drawn_image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(drawn_image)

    try:
        transformed_points = points.copy()
        valid_points_indices = (transformed_points[:, 0] >= 0) & (transformed_points[:, 0] < width) & \
                               (transformed_points[:, 1] >= 0) & (transformed_points[:, 1] < height)
        valid_points = transformed_points[valid_points_indices]

        if point_size == 1:
            draw.point([tuple(p) for p in valid_points.astype(int)], fill=point_color)
        else:
            for x, y in valid_points.astype(int):
                x0 = x - point_size // 2
                y0 = y - point_size // 2
                x1 = x + (point_size - point_size // 2)
                y1 = y + (point_size - point_size // 2)
                draw.ellipse([(x0, y0), (x1, y1)], fill=point_color)

        return drawn_image
    except Exception as e:
        print(f"Błąd podczas rysowania punktów: {e}")
        return Image.new('RGB', (width, height), color='red')
def draw_contours_as_lines(list_of_contour_arrays, image_pil, line_color=(0, 0, 0), line_width=1):
    if image_pil is None:
        return Image.new('RGB', (512, 512), color='white')

    width, height = image_pil.size

    if not list_of_contour_arrays:
        return Image.new('RGB', (width, height), color='white')

    drawn_image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(drawn_image)

    try:
        for contour in list_of_contour_arrays:
            if contour is None or len(contour) < 2:
                continue

            image_coords = contour.copy()
            image_coords = image_coords.astype(int)

            points_for_drawing = [(p[0], p[1]) for p in image_coords]

            if len(points_for_drawing) >= 2:
                draw.line(points_for_drawing, fill=line_color, width=line_width)
                draw.line([points_for_drawing[-1], points_for_drawing[0]], fill=line_color, width=line_width)

        return drawn_image
    except Exception as e:
        print(f"Błąd podczas rysowania konturów: {e}")
        return Image.new('RGB', (width, height), color='red')
def generate_and_display(prompt, width, height, kernel, thresh1, thresh2, min_area, device, status_label, frame, max_points,shm_name):
    def _thread():
        s2 = ShareableList(name=shm_name)
        for widget in frame.winfo_children():
            widget.destroy()
        progress_var = tk.IntVar()
        progress_bar = ttk.Progressbar(frame, maximum=100, variable=progress_var, length=200)
        progress_bar.pack()
        status_label.config(text="Ładowanie modelu...")
        torch_device = {
            "cpu": torch.device("cpu"),
            "cuda": torch.device("cuda"),
            "directml": torch.device("dml") if torch.backends.mps.is_available() else torch.device("cpu")
        }[device]
        pipe = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5")
        pipe = pipe.to(torch_device)
        num_inference_steps = 50
        start_time = time.time()
        def callback(step, timestep, latents):
            elapsed = time.time() - start_time
            est_total = elapsed / (step + 1) * num_inference_steps
            remaining = est_total - elapsed
            percent = int((step + 1) / num_inference_steps * 100)
            def update_gui():
                progress_var.set(percent)
                progress_bar.update_idletasks()
                status_label.config(text=f"Postęp: {step+1}/{num_inference_steps}, ETA: {int(remaining)}s")
            frame.after(0, update_gui)
        status_label.config(text="Generowanie obrazu...")
        image = pipe(prompt, height=height, width=width, num_inference_steps=num_inference_steps, callback=callback, callback_steps=1).images[0]
        gray = ImageOps.grayscale(image)
        np_gray = np.array(gray)
        kernel_value = kernel if kernel % 2 == 1 else kernel + 1
        blurred = cv2.GaussianBlur(np_gray, (kernel_value, kernel_value), 0)
        edges = cv2.Canny(blurred, thresh1, thresh2)
        contours, _ = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contour_img = np.zeros_like(edges)
        selected_contours = []
        all_points = []
        for cnt in contours:
            if cv2.contourArea(cnt) >= min_area:
                cnt = cnt.squeeze(axis=1)
                if len(cnt.shape) == 1:
                    continue
                cv2.drawContours(contour_img, [cnt], -1, 255, 1)
                selected_contours.append(cnt)
                all_points.extend(cnt)
        all_points_np = np.array(all_points) if all_points else np.empty((0, 2), dtype=int)
        if all_points_np.shape[0] > max_points:
            step = max(1, all_points_np.shape[0] // max_points)
            all_points_np = all_points_np[::step][:max_points]
        np_image_rgb = np.array(image)
        np_image_bgr = cv2.cvtColor(np_image_rgb, cv2.COLOR_RGB2BGR)
        gray_for_direct = cv2.cvtColor(np_image_bgr, cv2.COLOR_BGR2GRAY) 
        _, thresh_for_direct = cv2.threshold(gray_for_direct, 127, 255, cv2.THRESH_BINARY)
        contours_B, _ = cv2.findContours(thresh_for_direct.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contour_B_color_bgr = np.zeros((height, width, 3), dtype=np.uint8)
        cv2.drawContours(contour_B_color_bgr, contours_B, -1, (255, 255, 255), 1)
        contour_B_pil = Image.fromarray(cv2.cvtColor(contour_B_color_bgr, cv2.COLOR_BGR2RGB))
        plotter_image = Image.new('RGB', image.size, color='white')
        draw_plotter = ImageDraw.Draw(plotter_image)
        PEN_DOWN_DIST_THRESHOLD = 60
        if len(all_points_np) > 1:
            start_idx = np.argmin(all_points_np[:, 0] + (image.size[1] - all_points_np[:, 1]))
            visited = [start_idx]
            unvisited = set(range(len(all_points_np))) - {start_idx}
            current_idx = start_idx
            current_point = tuple(map(int, all_points_np[current_idx]))
            pen_down = True
            while unvisited:
                next_points = all_points_np[list(unvisited)]
                dists = np.linalg.norm(next_points - all_points_np[current_idx], axis=1)
                next_rel_idx = np.argmin(dists)
                next_idx = list(unvisited)[next_rel_idx]
                next_point = tuple(map(int, all_points_np[next_idx]))
                dist = np.linalg.norm(np.array(current_point) - np.array(next_point))
                if dist > PEN_DOWN_DIST_THRESHOLD:
                    pen_down = False  # Podnieś pisak
                else:
                    if pen_down:
                        draw_plotter.line([current_point, next_point], fill=(0, 0, 0), width=1)
                    pen_down = True  # Opuść pisak
                current_point = next_point
                current_idx = next_idx
                visited.append(current_idx)
                unvisited.remove(current_idx)
        end_time = time.time()
        start_str = datetime.fromtimestamp(start_time).strftime('%H:%M:%S')
        end_str = datetime.fromtimestamp(end_time).strftime('%H:%M:%S')
        end_day = datetime.fromtimestamp(end_time).strftime('%Y-%m-%d')
        s2[32] = start_str
        s2[33] = end_str
        img_w = width
        img_h = height
        with open("punkty.txt", "w") as f:
            f.write(f"{prompt}\n")
            f.write(f"{start_str}\n")
            f.write(f"{end_str}\n")
            f.write(f"{end_day}\n")
            for pt in all_points_np:
                x_norm = pt[0] / img_w
                y_norm = pt[1] / img_h
                x_robot = -92.5 + x_norm * (36 - -56) + 70
                y_robot = -56 + y_norm * (36 - -56)
                f.write(f"{x_robot:.2f},{y_robot:.2f}\n")
        pil_points = draw_points_on_image(all_points_np, image_pil=image, point_color=(255, 0, 0), point_size=1)
        pil_images = [
            image,
            Image.fromarray(contour_img),
            gray,
            contour_B_pil
        ]
        titles = ["Oryginalny", "Kontury po przekształceniach", "Odcienie szarości" , "Kontury bezpośrednio", ]
        for widget in frame.winfo_children():
            widget.destroy()
        for img, title in zip(pil_images, titles):
            f = tk.Frame(frame)
            f.pack(side="left", padx=3)
            tk_img = ImageTk.PhotoImage(img.resize((128, 128)))
            lbl = tk.Label(f, image=tk_img)
            lbl.image = tk_img
            lbl.pack()
            tk.Label(f, text=title).pack()
        status_label.config(text="Gotowe.")
        s2[30] = 1
    threading.Thread(target=_thread).start()
class MyGui:
    def __init__(self,root,s1,shm_name):
        self.root = root
        self.s1 = s1
        self.buttons = []
        self.canvas = []
        self.shm_name = shm_name
        s2 = ShareableList(name=shm_name)
        self.create_stable_diffusion_panel(self.root)
        recznystxt = tk.Canvas(self.root,height=40,width= 130, bg='white')
        recznystxt.create_text(65,20,text = "Tryb", font=("tahoma",26), fill = 'black')
        recznystxt.insert(tk.END, 'Tryb', 'big')
        recznystxt.place(x=895,y = 320)
        recznytxt = tk.Canvas(self.root,height=40,width= 130, bg='white')
        recznytxt.create_text(65,20,text = "ON/OFF", font=("tahoma",26), fill = 'black')
        recznytxt.insert(tk.END, 'ON/OFF', 'big')
        recznytxt.place(x=745,y = 320)
        draw = tk.Button(self.root, text="NARYSUJ", bg='lightgray',height=2,width= 8, font=("tahoma",26),state= "disabled" if (s2[15]) else "normal", command=lambda: insertToDatabase(self,self.shm_name))
        draw.place(x=1200,y=850)
        self.draw = draw
        reczny_start = tk.Button(self.root, text=s2[28],bg='lightgray',height=2,width= 6, font=("tahoma",26), command = lambda : reczny_button(s1,s2,self.shm_name))
        reczny_start.place(x=750,y = 370)
        self.reczny_start = reczny_start
        kolo_start = tk.Button(self.root, text="O",bg='lightgray',height=2,width= 6, font=("tahoma",26), command = lambda : draw_circle(s1,s2,self.shm_name))
        kolo_start.place(x=250,y = 480)
        self.kolo_start = kolo_start
        iks_start = tk.Button(self.root, text="X",bg='lightgray',height=2,width= 6, font=("tahoma",26), command = lambda : draw_iks(s1,s2,self.shm_name))
        iks_start.place(x=375,y = 480)
        self.iks_start = iks_start
        kwadrat_start = tk.Button(self.root, text="Sqr",bg='lightgray',height=2,width= 6, font=("tahoma",26), command = lambda : draw_square(s1,s2,self.shm_name))
        kwadrat_start.place(x=500,y = 480)
        self.kwadrat_start = kwadrat_start
        osZ = tk.Button(self.root, text=s2[21],bg='lightgray',height=2,width= 6, font=("tahoma",26), command = lambda : z_button(s1,s2,self.shm_name))
        osZ.place(x=1050,y = 370)
        self.osZ= osZ
        reczny_label = tk.Label(self.root, text=s2[15], bg="lightyellow",height=2,width= 6,font=("tahoma",26))
        reczny_label.place(x=900,y = 370)
        self.reczny_label = reczny_label
        btn1 = tk.Button(self.root, text="1", name="button1",bg='lightgray',height=2,width= 6, font=("tahoma",26),state=s2[23], command=lambda: on_radio_click(btn1,self.shm_name))
        btn1.place(x=250,y=700)
        self.btn1 = btn1
        btn2 = tk.Button(self.root, text="10", name="button2",bg='lightgray',height=2,width= 6, font=("tahoma",26),state=s2[24], command=lambda: on_radio_click(btn2,self.shm_name))
        btn2.place(x=375,y=700)
        self.btn2 = btn2
        btn3 = tk.Button(self.root, text="50", name="button3",bg='lightgray',height=2,width= 6, font=("tahoma",26),state=s2[25], command=lambda: on_radio_click(btn3,self.shm_name))
        btn3.place(x=500,y=700)
        self.btn3 = btn3
        radiotxt = tk.Canvas(self.root,height=40,width= 130, bg='white')
        radiotxt.create_text(65,20,text = "Posuw:", font=("tahoma",26), fill = 'black')
        radiotxt.insert(tk.END, 'Posuw:', 'big')
        radiotxt.place(x=370,y = 650)
        canvas_size = 400
        canvaDPAD = tk.Canvas(self.root,height=canvas_size, width=canvas_size, bg='white')
        canvaDPAD.place(x=770,y=500)
        create_dpad(canvaDPAD,canvas_size // 2, canvas_size // 2, size= 60, callback=on_click,shm_name=shm_name)
        #Cykliczny update przycisków
        self.update1(s1,s2)
        self.root.mainloop()
    def update1(self, s1,s2):
        self.reczny_start.config(text=s2[28])
        self.reczny_label.config(text=s2[15])
        self.osZ.config(text=s2[21])
        self.btn1.config(state=s2[23])
        self.btn2.config(state=s2[24])
        self.btn3.config(state=s2[25])
        self.draw.config(state= "disabled" if (s2[15]) else "normal")
        self.root.after(300, lambda : self.update1(s1,s2))

    def create_stable_diffusion_panel(self, parent):
        frame = tk.LabelFrame(parent, text="Stable Diffusion", width=600)
        frame.place(x=1200, y=100)
        tk.Label(frame, text="Prompt:").pack()
        prompt_entry = tk.Entry(frame, width=40)
        prompt_entry.pack()
        tk.Label(frame, text="Renderer:").pack()
        device_var = tk.StringVar(value="cpu")
        tk.OptionMenu(frame, device_var, "cpu", "cuda", "directml").pack()
        width_var = tk.IntVar(value=256)
        height_var = tk.IntVar(value=256)
        tk.Label(frame, text="Wymiary obrazu:").pack()
        tk.Spinbox(frame, from_=64, to=1024, increment=8, textvariable=width_var).pack()
        tk.Spinbox(frame, from_=64, to=1024, increment=8, textvariable=height_var).pack()
        gauss_kernel = tk.IntVar(value=9)
        canny1 = tk.IntVar(value=100)
        canny2 = tk.IntVar(value=200)
        min_area = tk.IntVar(value=10)
        max_points_var = tk.IntVar(value=150)
        tk.Label(frame, text="Gauss Kernel:").pack()
        tk.Scale(frame, from_=1, to=21, resolution=2, orient="horizontal", variable=gauss_kernel).pack()
        tk.Label(frame, text="Canny Threshold1:").pack()
        tk.Scale(frame, from_=0, to=255, orient="horizontal", variable=canny1).pack()
        tk.Label(frame, text="Canny Threshold2:").pack()
        tk.Scale(frame, from_=0, to=255, orient="horizontal", variable=canny2).pack()
        tk.Label(frame, text="Min powierzchnia konturu:").pack()
        tk.Scale(frame, from_=5, to=100, orient="horizontal", variable=min_area).pack()
        tk.Label(frame, text="Max liczba punktów:").pack()
        max_points_var = tk.IntVar(value=1000)
        tk.Scale(frame, from_=50, to=1200, variable=max_points_var, orient="horizontal").pack()
        status_label = tk.Label(frame, text="Status: ")
        status_label.pack()
        canvas_frame = tk.Frame(frame)
        canvas_frame.pack()
        generate_button = tk.Button(frame, text="Generuj", command=lambda: generate_and_display(
            prompt_entry.get(), width_var.get(), height_var.get(),
            gauss_kernel.get(), canny1.get(), canny2.get(), min_area.get(),
            device_var.get(), status_label, canvas_frame, max_points_var.get(),self.shm_name
        ))
        generate_button.pack(pady=5)
def loop_b(s1,shm_name):
    #Deklaracja okna
    s2 = ShareableList(name=shm_name)
    root = tk.Tk()
    root.title("Robot")
    root.geometry('1920x1080')
    root.configure(background='white')
    obj = MyGui(root,s1,shm_name)
def calculateKinematics(x_,y_,shm_name,tryb):
    s2 = ShareableList(name=shm_name)
    # Długości ramion
    l1 = 171
    l2 = 170 
    l3 = 26 
    D = 94.5 # Odległość między bazą lewą a prawą
    if s2[11] == None and s2[12] == None:
        s2[11] = 0
        s2[12] = 0
    przesx = D/2 + 27
    przesy = 236
    if x_ < -18.5 - przesx:
        x_ = -18.5 - przesx
        s2[11] = -18.5 - przesx
    elif x_ > 190.5 - przesx:
        x_ = 190.5 - przesx
        s2[11] = 190.5 - przesx
    if y_ < 180 - przesy:
        y_ = 180 - przesy
        s2[12] = 180 - przesy
    elif y_ > 272 - przesy:
        y_ = 272 - przesy
        s2[12] = 272 - przesy
    x_ = x_ + przesx
    y_ = y_ + przesy
    vartheta = 120 * pi / 180
    l2_ = sqrt(l2**2 + l3**2 - 2 * l2 * l3 * cos(vartheta))
    varphi = acos((-l3**2 + l2_**2 + l2**2) / (2 * l2 * l2_))
    delta_ = atan2(y_, x_)
    c_ = sqrt(x_**2 + y_**2)
    gamma_ = acos((-(l2_)**2 + c_**2 + l1**2) / (2 * l1 * c_))
    alpha = delta_ + gamma_
    phi = acos((-(c_)**2 + l1**2 + l2_**2) / (2 * l1 * l2_)) - varphi
    theta = alpha + phi + vartheta
    x = x_ + l3 * sin(theta - pi / 2)
    y = y_ - l3 * cos(theta - pi / 2)
    e = sqrt((D - x)**2 + y**2)
    psi = atan2(y, (D - x))
    epsilon = acos((-(l2)**2 + e**2 + l1**2) / (2 * l1 * e))
    beta = (pi - psi - epsilon)
    if tryb =='AUTO':
        s2[5] = int(alpha*180/pi)
        s2[6] = int(beta * 180/pi)
        s2[7] = int(gamma_ * 180/pi)
        s2[8] = int(phi*180/pi)
    if tryb =='RECZNY':
        s2[13] = round(alpha*180/pi,2)
        s2[14] = round(beta * 180/pi,2)
# Przekształcenie otrzymanej ramki na liczbę dziesiętną
def bin_to_dec(bArray):
    newBA = bArray.tolist()
    wynik = 0
    for i in range(len(newBA)):
        wynik += newBA[7-i]*2**i
    return wynik
# Zamiana z dec na bin
def dec_to_bin(number):
    lista = []
    while number > 0:
        num = number % 2
        number = number//2
        lista.insert(0,num)
    if len(lista) < 8:
        for i in range(8-len(lista)):
            lista.insert(0,0) #Uzupełnienie zerami wiodącymi
    return lista
def process_a1(broker, port, topic, client_id, s1,shm_name):
    mqtt_client = MyMQTT1(broker, port, topic, client_id, s1,shm_name)
    mqtt_client.loop_d(shm_name,s1)
if __name__ == '__main__':
    broker = "localhost"
    port = 1883
    topic = "testTopic"
    topic1 = 'pozycje'
    client_id_a = "client_a_unique"
    client_id_b = "client_b_unique"
    mem_name = "shared_memory_name"
    mem1 = SharedMemoryManager()
    mem1.start()
    mem2 = SharedMemoryManager()
    mem2.start()
    s1 = mem1.ShareableList([None,None,None,None,None,None,None,None,None,"Start", "","",""])
    s2 = mem2.ShareableList(["",None,0,0,0,None,None,None,None,"","",None,None,None,None,1,None,None,None,0,"Opusc","Opusc","1","disabled","normal","normal",None,"","AUTO",0,0,"","","",""])
    calculateKinematics(75,100,s2.shm.name,'AUTO')
# Deklaracja procesów i odpowiadających im funkcji( w target= podajemy funkcje, a w args= parametry do jej wywołania ( w tym przypadku nazwę pamięci))
    process_a = Process(target=process_a1, args=(broker, port, topic, client_id_a,s1,s2.shm.name,))
    process_b = Process(target=loop_b, args=((s1,s2.shm.name,)))
# Odpalenie procesów
    process_a.start()
    process_b.start()
# Połączenie procesów
    process_a.join()
    process_b.join()
# Zamknięcie pamięci
    s1.shm.close()
    s1.shm.unlink()