from LabOptic import *
import numpy as np
import time

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.set_xlabel("$x, \mu m$")
ax.set_ylabel("$y, \mu m$")
ax.set_xlim(0, 80)
ax.set_ylim(0, 80)
ax.set_aspect('equal') 
ax.grid()


# Метод, который определяет количество углов многоугольника, который близок к окружности радиуса R
def count_point(R):
    c = 1                           # Длина стороны многоугольника (определяет часоту точек)
    phi = 2 * np.arcsin(c/(2*R))      
    return np.round(np.pi/phi)+1


# Метод, который рисует окружность радиуса R, с периодом T, с координатами центра (x_0, y_0) на грфике
def plot_circle(R=20, T=2.0, x0 = 20, y0=20):              
    dt = T/count_point(R)   # Определяем промежуток времни между сигналами
    omega = 2 * np.pi / T   # Угловая скорость [1/s]

    # Определяю количество точек на кругу
    t = np.arange(0, T+dt, dt)

    # Массив для координат радиуса
    r = np.empty((t.size, 2))

    # Определяю координату каждой точки в каждый заданный момент времени 
    r[:, 0] = x0 + np.round(R * np.cos(omega * t), 2)
    r[:, 1] = y0 + np.round(R * np.sin(omega * t), 2)

    plt.plot(r[:, 0], r[:, 1]) 

    
# Анимация движения по окружности радиуса R, с периодом T, с координатами центра (x_0, y_0)
def animation_circle(R=20, T=2.0, x = 40, y = 40):
    # Parameter der Simulation
    dt = T/count_point(R)           # Zeitschtittweite [s]
    omega = 2 * np.pi / T   # Winkelgeschwindigkeit [1/s]

    # Erzeuge ein Array von Zeitpunkten für einen Umlauf
    t = np.arange(0, T+dt, dt)

    #Erzeuge ein leeres n x 2 - Array für die Ortsvektoren
    r = np.empty((t.size, 2))

    # Erzeuge die Position des Massenpunktes für jeden Zeitpunkt
    r[:, 0] = x + R * np.cos(omega * t)
    r[:, 1] = y + R * np.sin(omega * t)

    # Erzeuge eine Figure und ein Axes-Object

    # Erzeuge einen leeren Plot für die Kreisbahn
    plot, = ax.plot([], [])

    # Erzeuge leere Punktplot
    punkt, = ax.plot([], [], 'o', color='red')

    def update(n):

        plot.set_data(r[:n + 1, 0], r[:n + 1, 1])

        punkt.set_data(r[n])
        return plot, punkt

    ani = mpl.animation.FuncAnimation(fig, update, interval=dt*1000, frames=t.size, blit='True')
    ani.save("Kreis.gif",  writer='imagemagick')


# Окружность для Пезы
# R - радиус окружности
# (x_0, y_0) - центр
def circle_Pesa(antaus, R=20, center_x = 40, center_y = 40):
    dt = 0.5                             # промежутки времени для подсчета координат (не влияет на результат)
    T = count_point(R) * dt              # Период
    omega = 2 * np.pi / T                # Угловая скорость [1/s]

    # Массив значений параметра t в которых будут подсчитаны координаты
    t = np.arange(0, T+dt, dt)

    # Двумерный массив для координат радиуса
    r = np.empty((t.size, 2))

    # Определяем позицию точки в каждый момент времени
    r[:, 0] = center_x + np.round(R * np.cos(omega * t), 2)
    r[:, 1] = center_y + np.round(R * np.sin(omega * t), 2)

    pesa_x = Pesa(0)
    pesa_y = Pesa(1)

    pesa_x.connect()
    pesa_y.connect()

    pesa_x.move(r[0, 0])
    pesa_y.move(r[0, 1])
    time.sleep(0.5)

    plot_circle(R, center_x, center_y)

    antaus.schutter_open()
    for i in range(1, t.size):
        pesa_x.move(r[i, 0])
        pesa_y.move(r[i, 1])
        time.sleep(0.05)                    # Время между отправкой комманд (определяет время нахождения лазера в точке)
    antaus.schutter_close()

    pesa_y.disconnect()
    pesa_x.disconnect()


# Массив окружностей (в одном столбце окружности одного радиуса)  для Пезы
# radii - массив радиусов
# powers - массив мощностей, при которых будут выжигаться окружности
# n - колиество строк 
# d - расстояние между окружнастями
def array_of_circles_Pesa(radii, powers, n=3, d=10):
    radii = np.array(radii)
    powers = np.array(powers)
    max_r = radii.max()

    l = (radii.size) * d
    for r in radii:
        l = l + r * 2
    if l > 80:
        raise Exception('The length of the array is greater than the length of the working surface (80 mk). Reduce the number of radii')
    l = max_r * n * 2 + n * d
    if l > 80:
        raise Exception('The length of the array is greater than the length of the working surface (80 mk). Reduce the number of circles')
    if d < 5:
        raise Exception('The distance between the circles cannot be less than 5 mk')
    if not powers.size == radii.size:
        raise Exception('The dimensions of the arrays of power and radii do not match')

    antaus = Antaus()
    
    for j in range(0, radii.size):
        for i in range(0, n):
            l = 0
            for k in range(0, j):
                l = l + radii[k]*2
            plot_circle(radii[j], x0 = d*(j+1)+l+radii[j], y0=d*(i+1)+max_r+2*max_r*i)
            antaus.set_power_trim(powers[j])
            circle_Pesa(antaus, radii[j], x0 = d*(j+1)+l+radii[j], y0=d*(i+1)+max_r+2*max_r*i)



# Линия для Пезы
# (x_0, y_0) - start
# (x, y) - end
def line_Pesa(antaus, x_0, y_0, x, y):
    pesa_x = Pesa(0)
    pesa_y = Pesa(1)
    dr = 2 # координатный шаг
    dt = 0.8 # временной шаг 


    l = np.sqrt((x-x_0)**2 + (y-y_0)**2)
    n = l / dr
    if x > x_0:
        x_cords = np.arange(x_0, x+x/n, abs(x-x_0)/n)
    elif x == x_0:
        pass
    else: 
        x_cords = np.arange(x+x/n, x_0, abs(x-x_0)/n)
        x_cords = -np.sort(-x_cords)

    if y>y_0:
        y_cords = np.arange(y_0, y+y/n, abs(y-y_0)/n)
    elif y == y_0:
        y_cords = np.ones(x_cords.size) * y 
    else: 
        y_cords = np.arange(y+y/n, y_0, abs(y-y_0)/n)
        y_cords =  -np.sort(-y_cords)

    if x == x_0:
        x_cords = np.ones(y_cords.size) * x 

    pesa_x.connect()
    pesa_y.connect()

    pesa_x.move(x_cords[0])
    pesa_y.move(y_cords[0])

    antaus.schutter_open()
    for i in range(0, x_cords.size):
        pesa_x.move(x_cords[i])
        pesa_y.move(y_cords[i])
        #antaus.schutter_open()
        time.sleep(dt)
        #antaus.schutter_close()
    antaus.schutter_close()

    pesa_x.disconnect()
    pesa_y.disconnect()

    plt.plot([x_0, x], [y_0, y])


# Сетка для Пезы
# m - количество столбцов
# n - количество строк
# x - ширина столбцов
# y - высота строк
# (x_0, y_0) - координаты нижнего левого угла
def grid_Pesa(antaus, n, m, dx, dy, x_0, y_0):
    x = x_0 + dx*m  # x-x_0 - ширина сетки
    y = y_0 + dy*n  # y-y_0 - высота сетки
    print(y)
    print(x)
    for i in range(0, m+1):
        line_Pesa(antaus, x_0+i*dx, y_0, x_0 + i*dx, y)
        plt.plot([x_0+i*dx, x_0+i*dx], [y_0, y])
        time.sleep(0.5)

    for i in range(0, n+1):
        line_Pesa(antaus, x_0, y_0+i*dy, x, y_0+i*dy)
        plt.plot([x_0, x], [y_0+i*dy, y_0+i*dy])
        time.sleep(0.5)
  

# Сердце для Пезы
# 2*l - ширина сердца
# (center_x, center_y) - нижний уголок сердца         
def heart_Pesa(antaus, l=20, center_x = 40, center_y = 40):
    T = 4*l                 # Количество точек
    omega = 2 * np.pi / T   # Угловая скорость [1/s]

    # Erzeuge ein Array von Zeitpunkten für einen Umlauf
    t = np.arange(0, T+1, 1)

    #Erzeuge ein leeres n x 2 - Array für die Ortsvektoren
    r = np.empty((t.size, 2))

    # Erzeuge die Position des Massenpunktes für jeden Zeitpunkt
    r[:, 0] = center_x + l*np.round(np.cos(t), 2)
    r[:, 1] = center_y + 1 + l*0.7*np.round(np.sin(t)+np.sqrt(abs(np.cos(t))), 2)

    pesa_x = Pesa(0)
    pesa_y = Pesa(1)

    pesa_x.connect()
    pesa_y.connect()

    pesa_x.move(r[0, 0])
    pesa_y.move(r[0, 1])


    for i in range(1, t.size): 
        pesa_x.move(r[i, 0])
        pesa_y.move(r[i, 1])
        antaus.schutter_open()
        time.sleep(0.2)
        antaus.schutter_close()
        time.sleep(0.2)

    
    pesa_y.disconnect()
    pesa_x.disconnect()

    plt.scatter(r[:, 0], r[:, 1])


# Линия для Ximc
# (x_0, y_0) - start
# (x, y) - end
def line_Ximc(antaus, x_0, x, y, id):
    ximc = Ximc(id)
    dr = 5 # координатный шаг
    dt = 2 # временной шаг 

    # перемещение на другой уровень
    if id == 2:
        ximc_y = Ximc(0)
        ximc_y.connect()
        ximc_y.move(y, 0)
        ximc_y.disconnect()
    elif id==0: 
        ximc_y = Ximc(2)
        ximc_y.connect()
        ximc_y.move(y, 0)
        ximc_y.disconnect()

    ximc.connect()

    ximc.move(x_0, 0)
    time.sleep(dt)                  # время на смещение в координату x_0
    antaus.schutter_open()  
    time.sleep(dt)                  # время на отправку запроcу антауса
    ximc.move(x, 0)
    time.sleep((x-x_0)/50)          # время работы антауса
    antaus.schutter_close()

    ximc.disconnect()


# Сетка для Ximc
# m - количество столбцов
# n - количество строк
# x - ширина столбцов
# y - высота строк
# (x_0, y_0) - координаты нижнего левого угла
def grid_Ximc(antaus, n, m, dx, dy, x_0, y_0):
    x = x_0 + dx*m  # x-x_0 - ширина сетки
    y = y_0 + dy*n  # y-y_0 - высота сетки


    for i in range(0, m+1):
        line_Ximc(antaus, y_0, y, x_0+i*dx, 2)
        plt.plot([x_0+i*dx, x_0+i*dx], [y_0, y])
        time.sleep(0.5)

    for i in range(0, n+1):
       
        line_Ximc(antaus, x_0, x, y_0+i*dy, 0)
        plt.plot([x_0, x], [y_0+i*dy, y_0+i*dy])
        time.sleep(0.5)


