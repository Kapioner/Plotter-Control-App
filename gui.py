import tkinter as tk
from multiprocessing.shared_memory import ShareableList

from widgets_and_insert import (insertToDatabase, reczny_button, draw_circle, draw_iks, 
                    draw_square, z_button, on_radio_click, on_click)
from imageGeneration import generate_and_display

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