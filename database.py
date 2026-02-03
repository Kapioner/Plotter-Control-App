from datetime import datetime
import psycopg
from multiprocessing.shared_memory import ShareableList

con = psycopg.connect(
   dbname="robot_new",
   user="postgres",
   password="Kacpry",
   host="localhost",
   port= '5432'
   )

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