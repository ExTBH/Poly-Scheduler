from datetime import *
import numpy as np
dt1s = datetime.strptime('6:00 AM', '%I:%M %p')
dt1e = datetime.strptime('9:00 AM', '%I:%M %p')

dt2s = datetime.strptime('9:01 AM', '%I:%M %p')
dt2e = datetime.strptime('9:50 AM', '%I:%M %p')

f1 = (dt1s.hour * 60 + dt1s.minute) / 10
s1 = int(
    f1 if f1.is_integer() else np.ceil(f1)
    )
f1 = (dt1e.hour * 60 + dt1e.minute) / 10
s2 = int(
    f1 if f1.is_integer() else np.ceil(f1)
    )
f1 = (dt2s.hour * 60 + dt2s.minute) / 10
s3 = int(
    f1 if f1.is_integer() else np.ceil(f1)
    )
f1 = (dt2e.hour * 60 + dt2e.minute) / 10
s4 = int(
    f1 if f1.is_integer() else np.ceil(f1)
    )

# print (s1, s2, s3, s4)
r1 = list(range(s1 * 2, s2 * 2 +1))
r2 = list(range(s3 * 2, s4 * 2 +1))

v1 = np.zeros(144 * 2, dtype=bool)
np.put(v1, r1, np.ones(s2-s1, dtype=bool))

v2 = np.zeros(144 * 2, dtype=bool)
np.put(v2, r2, np.ones(s4-s3, dtype=bool))
# print(np.sum(v1*v2))

mtrx = np.array([v1, v2])
for mtrc in mtrx:
    for inner_mtrc in mtrx:
        if np.array_equal(inner_mtrc, mtrc) == False:
            clashes = np.sum(mtrc * inner_mtrc, dtype=bool)
            print(clashes)