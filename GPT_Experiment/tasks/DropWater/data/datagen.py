import random

def gao(op, x, y, a, b):
    if op=='fill_a':
        return a, y
    if op=='fill_b':
        return x, b
    if op=='empty_a':
        return 0, y
    if op=='empty_b':
        return x, 0
    if op=='a_to_b':
        t = min(x, b-y)
        return x-t, y+t
    if op=='b_to_a':
        t = min(y, a-x)
        return x+t, y-t
    assert 0

data = []

for a in range(5, 30):
    for b in range(a+1, 30):
        vis = []
        for i in range(a+1):
            vis.append([-1]*(b+1))
        nv = [-1]*(max(a,b)+1)
        que = [(0,0)]
        vis[0][0] = 0
        nv[0] = 0
        while len(que):
            x, y = que[0]
            que = que[1:]
            d = vis[x][y]
            
            if nv[x]==-1:
                nv[x] = d
                if d>=2 and d<=4:
                    data.append((a,b,x,d))
            if nv[y]==-1:
                nv[y] = d
                if d>=2 and d<=4:
                    data.append((a,b,y,d))
            
            if d==6: continue
            
            for op in ['fill_a', 'fill_b', 'empty_a', 'empty_b', 'a_to_b', 'b_to_a']:
                xx, yy = gao(op, x, y, a, b)
                if vis[xx][yy]==-1:
                    vis[xx][yy] = d+1
                    que.append((xx,yy))

print(len(data))
tot = len(data)
random.shuffle(data)

def data_to_string(data):
    sb = [f'{a} {b} {g} {d}' for a, b, g, d in data]
    return '\n'.join(sb)

open('train.txt', 'w').write(data_to_string(data[tot//8:]))
open('valid.txt', 'w').write(data_to_string(data[:tot//8]))