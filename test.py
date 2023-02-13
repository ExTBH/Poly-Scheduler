from datetime import *
import itertools
dt1s = datetime.strptime('6:00 AM', '%I:%M %p')
dt1e = datetime.strptime('9:00 AM', '%I:%M %p')

dt2s = datetime.strptime('6:00 AM', '%I:%M %p')
dt2e = datetime.strptime('9:50 AM', '%I:%M %p')


if dt1s <= dt2e and dt1e >= dt2s:
    print('overlap')

if dt2s <= dt1s:
    print('It is before')

l1 = [list(range(1, 20)), list(range(1, 20)), list(range(1, 21))]



for pool in itertools.product(*[x for x in l1]):
    print (pool)