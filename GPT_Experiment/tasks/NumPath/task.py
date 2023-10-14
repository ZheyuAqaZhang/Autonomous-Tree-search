from utils import *

def get_current_numbers(x, y):
    n1, n2, n3 = x.split()
    n1, n2, n3 = int(n1), int(n2), int(n3)
    current = n2
    steps = 0
    if y:
        current = int(extract(y.split('[')[-1])[-1])
        steps = y.count('op')
    return n1 - steps, current

propose_prompt = '''Let's discuss two mathematical operations:
op1: Converts a number 'x' to '2x' (doubling).
op2: Converts 'x' to 'x + 1' (incrementing).
Now you have an initial number. Your task is finding all possible next steps.
Here are some examples.
Input: 2
Possible next steps:
[2] -> (op1) -> [4]
[2] -> (op2) -> [3]
Input: 5
Possible next steps:
[5] -> (op1) -> [10]
[5] -> (op2) -> [6]
Input: 7
Possible next steps:
[7] -> (op1) -> [14]
[7] -> (op2) -> [8]
Input: {input}
Possible next steps:
'''

propose_prompt_zero_shot = '''Let's discuss two mathematical operations:
op1: Converts a number 'x' to '2x' (doubling).
op2: Converts 'x' to 'x + 1' (incrementing).
You have an initial number {input}. You should find all possible successors.
Your answer should span multiple lines, with each line presenting a distinct successor. Maintain this format:
[a] -> (op1) -> [b]
or
[a] -> (op2) -> [c]
Do not contain any other things in your response!
'''


value_prompt = '''Let's discuss two mathematical operations:
op1: Converts a number 'x' to '2x' (doubling).
op2: Converts 'x' to 'x + 1' (incrementing).
Your should estimate the probability that one number can be converted to another with given number of operations.
(Your response should be an integer between 0 and 100.)
Q: 6 to 12 with exactly 1 operation.
A: Probability = 90
Q: 34 to 34 with exactly 0 operation.
A: Probability = 100
Q: 14 to 15 with exactly 1 operation.
A: Probability = 90
Q: 2 to 5 with exactly 2 operation.
A: Probability = 60
Q: {input} to {goal} with exactly {n_op} operation.
A:'''

value_prompt_zero_shot = '''Let's discuss two mathematical operations:
op1: Converts a number 'x' to '2x' (doubling).
op2: Converts 'x' to 'x + 1' (incrementing).
You have an initial number {input}.
The goal is {goal}.
The number of operations is exactly {n_op}.
Your should estimate the probability.
(Your response should be an integer between 0 and 100. Do not contain any other things in your response!)'''

class TASKNumPath(TASK):
    def __init__(self):
        super().__init__()
        self.name = 'NumPath'
    
    def get_steps(self, line):
        n1, n2, n3 = line.split()
        return int(n1)
    
    def prompt_input(self, line):
        n1, n2, n3 = line.split()
        return f'''Picture a set of numbers ranging from 1 to 100. Let's discuss two mathematical operations:
op1: Converts a number 'x' to '2x' (doubling).
op2: Converts 'x' to 'x + 1' (incrementing).
Your task is to generate a sequence of exactly {n1} conversions (whether more or less, is not permissible), beginning from {n2} and ending at {n3}.

Please solve this problem step by step.
Remember you need to have a summary in the last line of your reply: [number] -> [number] -> [number] -> ... -> [number] (the first number should be {n2}, the last number should be {n3}, and the number of arrows should be {n1})
For example, convert 1 to 10 with 4 steps, your last line may be: 1 -> 2 -> 4 -> 5 -> 10
'''
    
    def check_conclu(self, line, conclusion):
        # print('check_conclusion',line,conclusion)
        n1, n2, n3 = line.split()
        n1, n2, n3 = int(n1), int(n2), int(n3)
        washed = ''
        cnt = 0
        for char in conclusion:
            if char == ')':
                cnt -= 1
            if cnt == 0:
                washed += char
            if char == '(':
                cnt += 1
        numbers = extract(washed)
        if len(numbers) < n1 + 1: return 0
        numbers = numbers[-(n1+1):]
        if diff(numbers[0], n2): return 0
        if diff(numbers[-1], n3): return 0
        for s, t in zip(numbers[:-1], numbers[1:]):
            if diff(s+1, t) and diff(s*2, t):
                return 0
        return 1
    
    def wash_out(self, out):
        if out.count('->') <= 8 and (out.count('-> (op1) ->') + out.count('-> (op2) ->')):
            lines = out.split('\n')
            res = lines[0]
            for li in lines[1:]:
                res += ' ' + li[li.find('->'):]
            return res
        else:
            return out

    def propose_prompt_wrap(self, x: str, y: str='') -> str:
        current_step, current_numbers = get_current_numbers(x, y)
        prompt = (propose_prompt if self.shot>0 else propose_prompt_zero_shot).format(input=current_numbers)
        return prompt
    
    def value_prompt_wrap(self, x: str, y: str) -> str:
        current_step, current_numbers = get_current_numbers(x, y)
        n1, n2, goal = x.split()
        n1, n2, goal = int(n1), int(n2), int(goal)
        return (value_prompt if self.shot>0 else value_prompt_zero_shot).format(input=current_numbers, goal=goal, n_op=current_step)
    
    def value_outputs_unwrap(self, x: str, y: str, value_outputs: list) -> float:
        value = sum([abs(float(n)) for n in re.findall(r'[-+]?[0-9]*\.?[0-9]+', x)][-1] for x in value_outputs)/len(value_outputs)
        return value