from Positioner import PositionerValues
import numpy as np
positions = np.load(f"../data/positions-20241106074129.npy", allow_pickle=True)

print(positions[0].x)
print(positions[0].y)
print(positions[0].z)
