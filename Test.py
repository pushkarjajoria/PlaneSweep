import numpy as np

from InputHandler import LineSegment, PointType, PlaneSweepInput
from PlaneSweep import PlaneSweep
import time

n = 1000
lines = []
for i in range(n):
    slope = np.random.randint(0,20)
    y_int = np.random.uniform(-10,10)
    t1, t2 = np.random.uniform(0, 100, 2)
    if t1 > t2:
        t1, t2 = t2, t1
    lineseg = LineSegment(slope, y_int, t1,t2)
    lines.append(lineseg)

intersection = 0
intersecting_point = []

# Checking Intersections by brute force
st = time.time()
for i in range(len(lines)):
    for j in range(i+1, len(lines)):
        intersec = lines[i].compute_intersection(lines[j])
        if intersec.p_type == PointType.INTERSECTION:
            intersection += 1
            intersecting_point.append(intersec)
print("Brute force time taken: {}".format(time.time() - st))
print(intersection)
# for p in intersecting_point:
#     print(p.toString())

st = time.time()
psw_input = PlaneSweepInput(lines, [])
planesweep = PlaneSweep(psw_input)
intersections = planesweep.run()
print("PlaneSweep time taken: {}".format(time.time() - st))
print(len(intersections))
# for p in intersections:
#     print(p.toString())
