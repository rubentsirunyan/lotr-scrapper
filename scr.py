import json
import sys


with open('asd.json', 'r') as f:
    _dict = json.load(f)

_set = set()
for i in _dict:
    try:
        for j in i['Race']:
            if j == sys.argv[1]:
                print(i)
            _set.add(j)
    except KeyError:
        pass

l = sorted(_set)
for i in l:
    print i
