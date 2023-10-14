from utils import *


def get_current_numbers(x, y):
    numbers = extract(y.split('[')[-1]) if y else extract(x)[:-1]
    numbers.sort()
    return ' '.join([str(n) for n in numbers])

propose_prompt = '''Given some numbers, select two of them for one of the four arithmetic operations, and leave the other numbers unchanged.
Input: 1 3 6 9
Possible next steps:
[1, 3, 6, 9] -> (1 + 3 = 4) -> [4, 6, 9]
[1, 3, 6, 9] -> (1 * 3 = 3) -> [3, 6, 9]
[1, 3, 6, 9] -> (9 / 3 = 3) -> [1, 3, 6]
[1, 3, 6, 9] -> (3 * 6 = 18) -> [1, 9, 18]
[1, 3, 6, 9] -> (3 - 1 = 2) -> [2, 6, 9]
Input: 2 12 18
Possible next steps:
[2, 12, 18] -> (12 / 2 = 6) -> [6, 18]
[2, 12, 18] -> (2 + 12 = 14) -> [14, 18]
[2, 12, 18] -> (2 * 12 = 24) -> [18, 24]
[2, 12, 18] -> (12 - 2 = 10) -> [10, 18]
Input: 4 6
Possible next steps:
[4, 6] -> (4 * 6 = 24) -> [24]
[4, 6] -> (4 + 6 = 10) -> [10]
[4, 6] -> (6 - 4 = 2) -> [2]
Input: {input}
Possible next steps:
'''

propose_prompt_zero_shot = '''Given some numbers, select two of them for one of the four arithmetic operations, and leave the other numbers unchanged.
The numbers are: {input}.
Your answer should span multiple lines, with each line presenting a distinct solution. Maintain this format:
[a, b, c] -> (a + b = d) -> [c, d]
or
[a, b] -> (a * b = c) -> [c]
Note the usage of "[]" to enclose number sets and "()" for arithmetic equations, all linked by "->".
Do not contain any other things in your response!
'''


value_prompt = '''Given some numbers and a goal, you can use arithmetic to combine them. Estimate how probabily to result in the goal. (Your answer should be an integer between 0 and 100)
Q: 6 12 to get 18
A: Probability = 90
Q: 6 to get 8
A: Probability = 0
Q: 2 3 4 to get 24
A: Probability = 40
Q: {input} to get {goal}
A:'''

value_prompt_zero_shot = '''Given some numbers and a goal, you can use arithmetic to combine them. Estimate how probabily to result in the goal.
The numbers are {input}.
The goal is {goal}.
Your should estimate the probability.
(Your response should be an integer between 0 and 100. Do not contain any other things in your response!)'''

class TASKthreetoN(TASK):
    def __init__(self):
        super().__init__()
        self.name = 'threetoN'
        self.steps = 2
    
    def prompt_input(self, line):
        n1, n2, n3, goal = line.split()
        return f'''Solve the {goal}-point puzzle. You are given three numbers: {n1}, {n2} and {n3}. Perform two steps as follows:
Choose two numbers and use one of the four arithmetic operations to replace the two numbers with the result you get.
The final claim should be {goal}.

Please solve this problem step by step.
Remember you need to have a summary in the last line of your reply: [a1, a2, a3] -> (operation) -> [b1, b2] -> (operation) -> [c1]
For example, [2, 3, 6] get 24, your last line may be: [2, 3, 6] -> (2 + 6 = 8) -> [3, 8] -> (3 * 8 = 24) -> [24]
'''
    
    def check_conclu(self, line, conclusion):
        if conclusion.count('[') < 3: return 0
        newc = ''
        for i in range(len(conclusion)):
            if conclusion[i+1:].count('[') < 3:
                newc += conclusion[i]
        conclusion = newc
        if conclusion.count('[') != 3: return 0
        if conclusion.count(']') != 3: return 0
        if conclusion.count('->') != 4: return 0
        a, b, c, d = line.split()
        a, b, c, d = int(a), int(b), int(c), int(d)
        group1 = conclusion.split('[')[1].split(']')[0]
        group2 = conclusion.split('[')[2].split(']')[0]
        group3 = conclusion.split('[')[3].split(']')[0]
        eq1 = conclusion.split('->')[1].split('(')[1].split(')')[0]
        eq2 = conclusion.split('->')[3].split('(')[1].split(')')[0]
        try:
            group1 = eval(f'[{group1}]')
            group2 = eval(f'[{group2}]')
            group3 = eval(f'[{group3}]')
            if eval(eq1.replace('=', '==')) == False: return 0
            if eval(eq2.replace('=', '==')) == False: return 0
            if same_set(group1, [a,b,c]) == False: return 0
            if same_set(group3, [d]) == False: return 0
            if same_set(group1 + extract(eq1.split('=')[1]), group2 + extract(eq1.split('=')[0])) == False: return 0
            if same_set(group2 + extract(eq2.split('=')[1]), group3 + extract(eq2.split('=')[0])) == False: return 0
        except:
            return 0
        return 1
    
    def wash_out(self, out):
        if out.count('->') == 4 and max([o.count('->') for o in out.split('\n')]) <= 2:
            lines = out.split('\n')
            return lines[0] + lines[1][lines[1].find('->'):]
        else:
            return out
    
    def propose_prompt_wrap(self, x: str, y: str='') -> str:
        current_numbers = get_current_numbers(x, y)
        prompt = (propose_prompt if self.shot>0 else propose_prompt_zero_shot).format(input=current_numbers)
        return prompt
    
    def value_prompt_wrap(self, x: str, y: str) -> str:
        current_numbers = get_current_numbers(x, y)
        n1, n2, n3, goal = x.split()
        return (value_prompt if self.shot>0 else value_prompt_zero_shot).format(input=current_numbers, goal=goal)
    
    def value_outputs_unwrap(self, x: str, y: str, value_outputs: list) -> float:
        value = sum([abs(float(n)) for n in re.findall(r'[-+]?[0-9]*\.?[0-9]+', x)][-1] for x in value_outputs)/len(value_outputs)
        return value