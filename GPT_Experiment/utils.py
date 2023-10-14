import re, openai, time, traceback

def call_gpt(messages, n=1):
    while True:
        try:
            response = openai.ChatCompletion.create(
                model='gpt-4-0613',
                messages=messages,
                temperature=0.7 if n>1 else 0.2,
                max_tokens=2666,
                request_timeout=600,
                n=n,
            )
            return (
                [choice["message"]["content"] for choice in response["choices"]],
                response["usage"]["prompt_tokens"],
                response["usage"]["completion_tokens"],
            )
        except:
            print(traceback.format_exc())
            time.sleep(10)

def extract(equation):
    numbers = [float(n) for n in re.findall(r'[-+]?[0-9]*\.?[0-9]+', equation)]
    return numbers

def diff(a, b):
    return abs(a-b) > 0.02

def same_set(S, T):
    S.sort()
    T.sort()
    if len(S) != len(T): return False
    for a, b in zip(S, T):
        if diff(a,b): return False
    return True

def maybe_conclusion(li):
    res = li.count('->')
    numbers = 0
    for i in range(0,10):
        numbers += li.count(str(i))
    return res or (numbers and (li.count('ans') or li.count('Ans')))

class TASK():
    def __init__(self): # all for tot
        self.completion_tokens = 0
        self.prompt_tokens = 0
        self.value_cache = {}
    
    def get_steps(self, line):
        return self.steps
    
    def prompt_input(self, line):
        assert 0
    
    def prompt_few_shot(self, group, shot):
        res = []
        for i in range(shot):
            res.append({
                "role": "user", "content": open(f'tasks/{self.name}/fewshot/{group}/{i}.in', 'r').read()
            })
            res.append({
                "role": "assistant", "content": open(f'tasks/{self.name}/fewshot/{group}/{i}.out', 'r').read()
            })
        return res
    
    def check_conclu(self, line, conclusion):
        assert 0
    
    def wash_out(self, out):
        return out
    
    def check(self, line, out):
        if out.count('# Answer') >= 2:
            out = '# Answer'.join(out.split('# Answer')[:2])
        out = self.wash_out(out)
        conclusion = ''
        for li in out.split('\n'):
            if not li.startswith('Input: '):
                if len(li) > 8 and maybe_conclusion(li):
                    conclusion = li
        # print('check', line, conclusion)
        return self.check_conclu(line, conclusion)

def get_task(task):
    if task == 'threetoN':
        from tasks.threetoN.task import TASKthreetoN
        return TASKthreetoN()
    if task == 'DropWater':
        from tasks.DropWater.task import TASKDropWater
        return TASKDropWater()
    if task == 'NumPath':
        from tasks.NumPath.task import TASKNumPath
        return TASKNumPath()
    if task == 'NumSplit':
        from tasks.NumSplit.task import TASKNumSplit
        return TASKNumSplit()

def prompt_global(group):
    if group == 'nct':
        return '''When you are solve a puzzle, if you can't ensure this step is the best for following steps, you should write down some possible scenarios to ensure a broad range of attempts. Here is an example of your response format:

Step 1
scenario 1, [initial state]-> (operation 1) [state 1]
scenario 2, [initial state]-> (operation 2) [state 2]

Step 2
scenario 1.1, [initial state]->[state 1]-> (operation 1) [state 1.1]
scenario 1.2, [initial state]->[state 1]-> (operation 2) [state 1.2]
scenario 2.1, [initial state]->[state 2]-> (operation 1) [state 2.1]
scenario 2.2, [initial state]->[state 2]-> (operation 2) [state 2.2]

Step 3
scenario 1.1.1, [initial state]->[state 1]->[state 1.1]-> (operation 1) [state 1.1.1]
(You should write around 8 lines for Step 3)

Step 4
scenario 1.1.1.1 ...
(You should write around 16 lines for Step 4)
...'''

    if group == 'dfs':
        return '''When you are solving a puzzle, if you find that a certain step cannot be successful, you should step back appropriately. Here is an example of your response format:

Step 1
[initial state]-> (operation) [state 1]

Step 2
[initial state]->[state 1]-> (operation) [state 2]

Step 3
[initial state]->[state 1]->[state 2]-> (operation) [state 3]

This is not the goal. Let's step back. Now it is [state 2].

Step 3 (revised)
[initial state]->[state 1]->[state 2]-> (operation) [state 3]

Let's step back. Now it is [state 2].

Let's step back. Now it is [state 1].

Step 2 (revised)
[initial state]->[state 1]-> (operation) [state 2]

...'''