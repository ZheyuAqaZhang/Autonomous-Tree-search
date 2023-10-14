import random

data = []

def suc(x):
    return [x*2, x+1]

for x0 in range(1, 21):
    for x1 in suc(x0):
        for x2 in suc(x1):
            for x3 in suc(x2):
                if x3<=100: data.append((3, x0, x3))
                for x4 in suc(x3):
                    if x4<=100:
                        data.append((4, x0, x4))

print(len(data))
tot = len(data)
random.shuffle(data)

def data_to_string(data):
    sb = [f'{a} {b} {c}' for a, b, c in data]
    return '\n'.join(sb)

open('train.txt', 'w').write(data_to_string(data[tot//8:]))
open('valid.txt', 'w').write(data_to_string(data[:tot//8]))