from LabOptic import *
from draw_methods import *

antaus = Antaus()
ximc_x = Ximc(0)
ximc_x.connect()
x_0 = ximc_x.get_position()[0]
ximc_x.disconnect()

ximc_x = Ximc(2)
ximc_x.connect()
y_0 = ximc_x.get_position()[0]
ximc_x.disconnect()

grid_Ximc(antaus, 3, 3, 80, 80, x_0, y_0)

#plt.show()
#antaus = Antaus()
#antaus.schutter_close()