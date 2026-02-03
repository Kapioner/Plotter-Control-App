from math import cos, atan2, acos, sin, sqrt, pi
from multiprocessing.shared_memory import ShareableList

def DegToRad(deg):
    return deg*pi/180

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

def rozmiesc(start, stop, num):
    if num < 2:
        return [start]
    step = (stop - start) / (num - 1)
    return [start + i * step for i in range(num)]

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