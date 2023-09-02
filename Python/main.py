from LabOptic import *
from draw_methods import *


# Включение лазера 
#antaus = Antaus()
#antaus.schutter_open()

# Выключение лазера
#antaus = Antaus()
#antaus.schutter_close()

# Изменение параметров лазера
#antaus = Antaus()
#antaus.set_base_divider(new_base_divider)
#antaus.set_freq_time(new_freg_time)
#antaus.set_power_trim(new_power)

# Сдвинуть подвижку (Ximc) на 100
#ximc = Ximc(Ximc_X) # Ximc_X, Ximc_Y, Ximc_Z коды определенны в методе draw_methods
#ximc.connect()
#cord = ximc.get_position()
#ximc.move(cord[0]+100, cord[1])
#ximc.disconnect()

#

# Пример использования метода из draw_methods
#antaus = Antaus()
#circle_Pesa(antaus, 10, 40, 40)


x_0 = 10
y_0 = 10
dx = 5
dy = 5
m = 5
n = 5

x = x_0 + dx*m  # x-x_0 - ширина сетки
y = y_0 + dy*n  # y-y_0 - высота сетки

ax = plt.axes()

colors = ['grey', 'black', 'red', 'green', 'orange', 'blue', 'pink']

# линии параллельно y
for i in range(0, m+1):
    if i%2==0:
        ax.arrow(x_0+i*dx, y_0,  dx=0, dy=y-y_0, head_width=0.2, head_length=0.5, fc=colors[i], ec=colors[i])
    else: 
        ax.arrow(x_0+i*dx, y,  dx=0, dy=y_0-y, head_width=0.2, head_length=0.5, fc=colors[i], ec=colors[i])

for i  in range(0, n+1):
    if m%2==0:
        if i%2 == 0:
            ax.arrow(x, y-i*dy, x_0-x, 0, head_width=0.3, head_length=0.7, fc=colors[i], ec=colors[i])
        else:
            ax.arrow(x_0, y-i*dy,  x-x_0, 0, head_width=0.3, head_length=0.7, fc=colors[i], ec=colors[i])
    else:
        if i%2 == 0:
            ax.arrow(x, y_0+i*dy, x_0-x, 0, head_width=0.3, head_length=0.7, fc=colors[i], ec=colors[i])
        else:
            ax.arrow(x_0, y_0+i*dy,  x-x_0, 0, head_width=0.3, head_length=0.7, fc=colors[i], ec=colors[i])
           
plt.show()

