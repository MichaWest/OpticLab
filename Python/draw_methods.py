from LabOptic import *
import numpy as np
import time

from Python.pesa import Pesa

Ximc_X = 0
Ximc_Y = 2
Ximc_Z = 1

Pesa_X = 0
Pesa_Y = 1
Pesa_Z = 2


# Метод, который определяет количество углов многоугольника, который близок к окружности радиуса R
def count_point(R):
    c = 1  # Длина стороны многоугольника (определяет часоту точек)
    phi = 2 * np.arcsin(c / (2 * R))
    return np.round(np.pi / phi) + 1


# Окружность для Пезы
# R - радиус окружности
# (x_0, y_0) - центр
def circle_Pesa(antaus, R=20, center_x=40, center_y=40):
    dt = 0.5  # промежутки времени для подсчета координат (не влияет на результат)
    T = count_point(R) * dt  # Период
    omega = 2 * np.pi / T  # Угловая скорость [1/s]

    # Массив значений параметра t в которых будут подсчитаны координаты
    t = np.arange(0, T + dt, dt)

    # Двумерный массив для координат радиуса
    r = np.empty((t.size, 2))

    # Определяем позицию точки в каждый момент времени
    r[:, 0] = center_x + np.round(R * np.cos(omega * t), 2)
    r[:, 1] = center_y + np.round(R * np.sin(omega * t), 2)

    pesa_x = Pesa(Pesa_X)
    pesa_y = Pesa(Pesa_Y)

    pesa_x.connect()
    pesa_y.connect()

    pesa_x.move(r[0, 0])
    pesa_y.move(r[0, 1])
    time.sleep(0.5)

    antaus.schutter_open()
    for i in range(1, t.size):
        pesa_x.move(r[i, 0])
        pesa_y.move(r[i, 1])
        time.sleep(0.05)  # Время между отправкой комманд (определяет время нахождения лазера в точке)
    antaus.schutter_close()

    pesa_y.disconnect()
    pesa_x.disconnect()



# Линия для Пезы
# (x_0, y_0) - start
# (x, y) - end
def line_Pesa(antaus, x_0, y_0, x, y):
    pesa_x = Pesa(Pesa_X)
    pesa_y = Pesa(Pesa_Y)
    dr = 2  # координатный шаг
    dt = 0.8  # временной шаг

    l = np.sqrt((x - x_0) ** 2 + (y - y_0) ** 2)
    n = l / dr
    if x > x_0:
        x_cords = np.arange(x_0, x + x / n, abs(x - x_0) / n)
    elif x == x_0:
        pass
    else:
        x_cords = np.arange(x + x / n, x_0, abs(x - x_0) / n)
        x_cords = -np.sort(-x_cords)

    if y > y_0:
        y_cords = np.arange(y_0, y + y / n, abs(y - y_0) / n)
    elif y == y_0:
        y_cords = np.ones(x_cords.size) * y
    else:
        y_cords = np.arange(y + y / n, y_0, abs(y - y_0) / n)
        y_cords = -np.sort(-y_cords)

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
        # antaus.schutter_open()
        time.sleep(dt)
        # antaus.schutter_close()
    antaus.schutter_close()

    pesa_x.disconnect()
    pesa_y.disconnect()


# Сетка для Пезы
# m - количество столбцов
# n - количество строк
# x - ширина столбцов
# y - высота строк
# (x_0, y_0) - координаты нижнего левого угла
def grid_Pesa(antaus, n, m, dx, dy, x_0, y_0):
    x = x_0 + dx * m  # x-x_0 - ширина сетки
    y = y_0 + dy * n  # y-y_0 - высота сетки
    print(y)
    print(x)
    for i in range(0, m + 1):
        line_Pesa(antaus, x_0 + i * dx, y_0, x_0 + i * dx, y)
        time.sleep(0.5)

    for i in range(0, n + 1):
        line_Pesa(antaus, x_0, y_0 + i * dy, x, y_0 + i * dy)
        time.sleep(0.5)


# Сердце для Пезы
# 2*l - ширина сердца
# (center_x, center_y) - нижний уголок сердца         
def heart_Pesa(antaus, l=20, center_x=40, center_y=40):
    T = 4 * l  # Количество точек
    omega = 2 * np.pi / T  # Угловая скорость [1/s]

    # Erzeuge ein Array von Zeitpunkten für einen Umlauf
    t = np.arange(0, T + 1, 1)

    # Erzeuge ein leeres n x 2 - Array für die Ortsvektoren
    r = np.empty((t.size, 2))

    # Erzeuge die Position des Massenpunktes für jeden Zeitpunkt
    r[:, 0] = center_x + l * np.round(np.cos(t), 2)
    r[:, 1] = center_y + 1 + l * 0.7 * np.round(np.sin(t) + np.sqrt(abs(np.cos(t))), 2)

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


# Линия для Ximc
def line_Ximc(antaus, ximc, x_0, x):
    dr = 5  # координатный шаг
    dt = 2  # временной шаг для учитывание задержек на отправку команд

    ximc.move_to(x_0, 0)
    # теперь заложено в методе move_to time.sleep(dt)                  # время на смещение в координату x_0
    antaus.schutter_open()
    time.sleep(dt)  # время на отправку запроcу антауса
    ximc.move_to(x, 0)
    # теперь заложено в методе move_to - time.sleep((abs(x-x_0))/70)          # время работы антауса
    antaus.schutter_close()


# Сетка для Ximc
# m - количество столбцов
# n - количество строк
# dx - ширина столбцов
# dy - высота строк
# (x_0, y_0) - координаты нижнего левого угла (для кода)
def grid_Ximc(antaus, ximc_x, ximc_y, n, m, dx, dy):
    x_0 = ximc_x.get_position()[0]
    y_0 = ximc_y.get_position()[0]

    x = x_0 + dx * m  # x-x_0 - ширина сетки
    y = y_0 - dy * n  # y-y_0 - высота сетки

    current_y = y_0
    current_x = x_0

    # змейка которая движется вверх
    for i in range(0, n + 1):
        if i % 2 == 0:
            line_Ximc(antaus, ximc_x, x_0, x)
            line_Ximc(antaus, ximc_y, current_y, current_y - dy)
            current_y = current_y - dy
            current_x = x
        else:
            line_Ximc(antaus, ximc_x, x, x_0)
            line_Ximc(antaus, ximc_y, current_y, current_y - dy)
            current_y = current_y - dy
            current_x = x_0
        time.sleep(0.5)

    # змейка которая движется влево или вправо
    if current_x == x:  # если мы оказались в правом верхнем углу, то движение будет в лево
        for i in range(0, m+1):
            if i % 2 == 0:
                line_Ximc(antaus, ximc_y, y, y_0)
                line_Ximc(antaus, ximc_x, current_x, current_x-dx)
                current_x = current_x - dx
                current_y = y_0
            else:
                line_Ximc(antaus, ximc_y, y_0, y)
                line_Ximc(antaus, ximc_x, current_x, current_x - dx)
                current_x = current_x - dx
                current_y = y
            time.sleep(0.5)
    else:
        for i in range(0, m+1):
            if i%2 == 0:
                line_Ximc(antaus, ximc_y, y, y_0)
                line_Ximc(antaus, ximc_x, current_x, current_x + dx)
                current_x = current_x + dx
                current_y = y_0
            else:
                line_Ximc(antaus, ximc_y, y_0, y)
                line_Ximc(antaus, ximc_x, current_x, current_x - dx)
                current_x = current_x - dx
                current_y = y
            time.sleep(0.5)

        time.sleep(0.5)


# Массив окружностей (в одном строке окружности одного радиуса)  Пеза рисует круги Ximc
# radii - массив радиусов
# powers - массив мощностей, при которых будут выжигаться окружности
# n - колиество строк 
# d - расстояние между окружнастями
def array_of_circles_PX(radii, powers, n=3, d=100):
    ximc_y = Ximc(Ximc_Y)  # ximc_x, ximc_y, ximc_z определенные в draw_methods
    ximc_x = Ximc(Ximc_X)  # ximc_x, ximc_y, ximc_z определенные в draw_methods
    ximc_x.connect()
    ximc_y.connect()

    antaus = Antaus()
    for j in range(0, radii.size):
        antaus.set_power_trim(powers[j])
        for i in range(0, n):
            circle_Pesa(antaus, radii[j], 40, 40)
            ximc_y.move(d)
        ximc_x.move(d)  # сдвиг вниз
        ximc_y.move(-d * n)  # сдвиг в начало строки

    ximc_x.disconnect
    ximc_y.disconnect()
