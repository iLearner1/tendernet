from _collections import defaultdict
from lots.insert_region_location import read_xls

d = read_xls()

codes = defaultdict(int)
names = defaultdict(int)

name_code_map = {}

for k, v in d.items():
    if k not in codes.keys():
        codes[k] += 1
    else:
        print("code exists: ", k)

    if v not in name_code_map.keys():
        name_code_map[v] = []
        name_code_map[v].append(k)
    else:
        name_code_map[v].append(k)

print(name_code_map)