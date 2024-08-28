from LabOptic import *
from Python.pesa import Pesa
from draw_methods import *

# Ximc_X = 0
# Ximc_Y = 2
# Ximc_Z = 1
#
# ximc_x = Ximc(Ximc_X)
# ximc_y = Ximc(Ximc_Y)
# ximc_z = Ximc(Ximc_Z)
#
# ximc_z.connect()
# ximc_y.connect()
# ximc_x.connect()
#
# ximc_x.set_speed(300)
# ximc_y.set_speed(300)
# ximc_z.set_speed(300)
#
# #используйте методы из draw_methods
#
# ximc_x.disconnect()
# ximc_y.disconnect()
# ximc_z.disconnect()

pesa = Pesa(0)  # x - 0, y - 1, z - 2
pesa.connect()

# методы для пезы из draw_methods
# heart_Pesa, grid_Pesa, line_Pesa, circle_Pesa

pesa.disconnect()
