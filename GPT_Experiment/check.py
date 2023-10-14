import fire, os, re, traceback
from utils import get_task
def extract(equation):
    numbers = [float(n) for n in re.findall(r'[-+]?[0-9]*\.?[0-9]+', equation)]
    return numbers

def check(task='threetoN', group='nct', shot=0, consistency=1, width=1, vote=False):
    env = get_task(task)
    tong = []
    token_prompt = []
    token_generate = []
    data = open(f'tasks/{task}/data/valid.txt','r').read().split('\n')
    GG = []
    for i, line in enumerate(data):
        if len(line)<2: continue
        try:
            if group == 'tot':
                file = f'tasks/{task}/output/{group}_{shot}shot_{consistency}cons_{width}width/valid/{i}.out'
            else:
                file = f'tasks/{task}/output/{group}_{shot}shot_{consistency}cons/valid/{i}.out'
            if consistency>1 and vote:
                ans = []
                for T in range(consistency):
                    ans.append(int(extract(open(file.replace('.out','_'+str(T)+'.out'), 'r').read())[-1]))
                idx = 0
                cnt = {}
                for x in ans:
                    if x not in cnt.keys():
                        cnt[x] = 0
                    cnt[x] += 1
                for i, x in enumerate(ans):
                    if cnt[x] > cnt[ans[idx]] or (cnt[x] == cnt[ans[idx]] and abs(x)<abs(ans[idx])):  # for finding minimal solution.
                        idx = i
                tong.append(env.check(line, open(file.replace('.out','_'+str(idx)+'.out'), 'r').read()))
            else:
                files = width if group=='tot' else consistency
                if files >= 200: files = 1
                if files==1 and os.path.exists(file):
                    tong.append(env.check(line, open(file, 'r').read()))
                else:
                    tong.append(max([env.check(line, open(file[:-4]+f'_{I}.out', 'r').read()) for I in range(files)]))
                    
            try:
                log = open(file.replace('.out','.log'), 'r').read()
            except:
                log = open(file.replace('.out','_0.log'), 'r').read()
            log = extract(log)
            token_prompt.append(log[0])
            token_generate.append(log[1])
        except:
            pass
            GG.append(i)
    
    if len(tong) == 0: return
    if group == 'tot':
        prefix = f'{task} {group}_{shot}shot_{consistency}cons_{width}width'
    else:
        prefix = f'{task} {group}_{shot}shot_{consistency}cons'
    if vote:
        prefix += '_vote'
    
    if len(token_generate)>0:
        avg_token_prompt = round(sum(token_prompt)/len(token_prompt),2)
        avg_token_generate = round(sum(token_generate)/len(token_generate),2)
        print(f'{prefix}  Accuracy:  {sum(tong)}/{len(tong)} = {sum(tong)/len(tong)}, token_prompt:  {avg_token_prompt}, token_generate:  {avg_token_generate}')
    else:
        print(f'{prefix}  Accuracy:  {sum(tong)}/{len(tong)} = {sum(tong)/len(tong)}')
    return

if __name__ == '__main__':
    fire.Fire(check)
