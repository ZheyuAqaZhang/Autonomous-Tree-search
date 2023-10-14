import random

ops = [(lambda x, y: x+y), (lambda x, y: x-y), (lambda x, y: x*y), (lambda x, y: (x/y if y!=0 else 1e9))]

def check(i, j, k, goal):
    nums = [i, j, k]
    for T in range(100):
        random.shuffle(nums)
        for a in ops:
            for b in ops:
                if b(a(i,j), k) == goal: return True
                if b(k, a(i,j)) == goal: return True
    return False

candidates = []

for goal in [6, 8, 12, 16, 18, 24]:
    for i in range(1, 13):
        for j in range(i, 13):
            for k in range(j, 13):
                if check(i, j, k, goal):
                    print(i, j, k, goal)
                    candidates.append(f'{i} {j} {k} {goal}')

random.shuffle(candidates)

n_eval = len(candidates)//5
open('valid.txt', 'w').write('\n'.join(candidates[:n_eval]))
open('train.txt', 'w').write('\n'.join(candidates[n_eval:]))
