from multiprocessing.shared_memory import ShareableList
from multiprocessing.managers import SharedMemoryManager
import math
import time
import json
from datetime import datetime
import numpy as np
from database import con, savePozAng
from kinematics import calculateKinematics, rozmiesc, cos, sin, pi
from communication import sendToRobot

def draw_circle(s1,s2,shm_name):
    if(s2[15]):
        s2[27] = 'KOLO'

def draw_iks(s1,s2,shm_name):
    if(s2[15]):
        s2[27] = 'iks'

def draw_square(s1,s2,shm_name):
    if(s2[15]):
        s2[27] = 'kwadrat'

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