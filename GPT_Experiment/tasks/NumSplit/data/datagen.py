import numpy as np

mp = {}
data = open('valid.txt', 'r').read().split('\n')
for o in data: mp[o] = 1

with open('train.txt','w') as f:
    for i in range(300):
        while True:
            a = np.random.randint(15,size=3)+1
            if (f'{a[0]} {a[1]} {a[2]}' in mp):
                print('G!')
                continue
            print(a[0],a[1],a[2],file=f)
            break

# with open('valid.txt','w') as f:
#     for i in range(100):
#         a = np.random.randint(15,size=3)+2 # 2..16
#         print(a[0],a[1],a[2],file=f)
#         print(a)