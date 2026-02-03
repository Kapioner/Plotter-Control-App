import time
import json
from paho.mqtt import client as mqtt_client
from multiprocessing.shared_memory import ShareableList
import numpy as np
from kinematics import calculateKinematics, rozmiesc
from database import con, savePozAng
from math import cos, atan2, acos, sin, sqrt, pi
from datetime import datetime
import math

def sendToRobot(self,shm_name):
    s2 = ShareableList(name=shm_name)
    wiad = {"th1": s2[13],"th2": s2[14], "z" : s2[19]}
    wys = json.dumps(wiad)
    self.client.publish('reczny',wys,qos=0)
    print("WYSLALANO Katy")
    print(f"Katy: {wiad}")  

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

def process_a1(broker, port, topic, client_id, s1,shm_name):
    mqtt_client = MyMQTT1(broker, port, topic, client_id, s1,shm_name)
    mqtt_client.loop_d(shm_name,s1)