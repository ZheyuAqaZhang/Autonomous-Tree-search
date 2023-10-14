from utils import *

def get_current_numbers(x, y):
    if y:
        a, b, c, d = extract(y)[-4:]
        return [int(a), int(b), int(c), int(d)] 
    else:
        n1, n2, n3, n4 = x.split()
        return [0,int(n1),0,int(n2)]

propose_prompt = '''# Environment
This game involves two empty bottles with capacities of {n1} and {n2} liters. There is also a large water reservoir.
You can do the following things:

1. Choose a bottle and proceed to fill it to its brim from the reservoir or conversely, empty it completely back into the reservoir. The following are some illustrative examples:
[0 / 7, 7 / 22] -> (fill the first) [7 / 7, 7 / 22];
[8 / 8, 11 / 19] -> (empty the first) [0 / 8, 11 / 19].

2. Pour water from one bottle into the other. This action concludes once the recipient bottle is at its full capacity or the source bottle is entirely empty. Here are some practical examples:
[0 / 7, 9 / 9] -> (pour the second to the first, it will halt by the full recipient) [7 / 7, 2 / 9];
[5 / 5, 5 / 7] -> (pour the first to the second, it will halt by the full recipient) [3 / 5, 7 / 7];
[12 / 12, 0 / 17] -> (pour the first to the second, it will halt by the empty source) [0 / 12, 12 / 17];

# Task
Now you are facing a task in this environment. Given a state, list some successive states.

Input: [0 / 5, 0 / 7]
Possible next steps:
[0 / 5, 0 / 7] -> [5 / 5, 0 / 7]
[0 / 5, 0 / 7] -> [0 / 5, 7 / 7]
Input: [0 / 12, 18 / 18]
Possible next steps:
[0 / 12, 18 / 18] -> [12 / 12, 6 / 18]
Input: [13 / 13, 13 / 16]
Possible next steps:
[13 / 13, 13 / 16] -> [10 / 13, 16 / 16]
[13 / 13, 13 / 16] -> [0 / 13, 13 / 16]
Input: [0 / 13, 13 / 16]
Possible next steps:
[0 / 13, 13 / 16] -> [13 / 13, 13 / 16]
Input: {input}
Possible next steps:
'''

propose_prompt_zero_shot = '''# Environment
This game involves two empty bottles with capacities of {n1} and {n2} liters. There is also a large water reservoir.
You can do the following things:

1. Choose a bottle and proceed to fill it to its brim from the reservoir or conversely, empty it completely back into the reservoir. The following are some illustrative examples:
[0 / 7, 7 / 22] -> (fill the first) [7 / 7, 7 / 22];
[8 / 8, 11 / 19] -> (empty the first) [0 / 8, 11 / 19].

2. Pour water from one bottle into the other. This action concludes once the recipient bottle is at its full capacity or the source bottle is entirely empty. Here are some practical examples:
[0 / 7, 9 / 9] -> (pour the second to the first, it will halt by the full recipient) [7 / 7, 2 / 9];
[5 / 5, 5 / 7] -> (pour the first to the second, it will halt by the full recipient) [3 / 5, 7 / 7];
[12 / 12, 0 / 17] -> (pour the first to the second, it will halt by the empty source) [0 / 12, 12 / 17];

# Task
Now you are facing a task in this environment. Given a state, list some successive states.

The current state of bottle is: {input}.
Your answer should span multiple lines, with each line presenting a distinct solution. Maintain this format:
[a / b, c / d] -> [e / f, g / h]
Note the usage of "[a / b, c / d]" should be the same as the bottle state.
Do not contain any other things in your response!
'''


value_prompt = '''# Game Description
This game involves two empty bottles with capacities of {n1} and {n2} liters. The objective is to collect exactly {n3} liters of water, using a large water reservoir.

Each step of the game offers you the choice to execute one of two actions:

Opt for a bottle and proceed to fill it to its brim from the reservoir or conversely, empty it completely back into the reservoir. The following are some illustrative examples:
[0 / 7, 7 / 22] -> (fill the first) [7 / 7, 7 / 22];
[8 / 8, 11 / 19] -> (empty the first) [0 / 8, 11 / 19].

Pour water from one bottle into the other. This action concludes once the recipient bottle is at its full capacity or the source bottle is entirely empty. Here are some practical examples:
[0 / 7, 9 / 9] -> (pour the second to the first, it will halt by the full recipient) [7 / 7, 2 / 9];
[5 / 5, 5 / 7] -> (pour the first to the second, it will halt by the full recipient) [3 / 5, 7 / 7];
[12 / 12, 0 / 17] -> (pour the first to the second, it will halt by the empty source) [0 / 12, 12 / 17];

# Your Task
Now you are facing a subtask of this game. Given a state, estimate how many steps to reach the goal {n3}.

Q: [8 / 8, 11 / 19] to get 11
A: Steps = 0
Q: [10 / 10, 10 / 29] to get 20
A: Steps = 1
Q: [0 / 20, 0 / 25] get 15
A: Steps = 4
Q: [0 / 11, 13 / 13] get 2
A: Steps = 1
Q: {input} to get {n4}
A:'''

value_prompt_zero_shot = '''This game involves two empty bottles with capacities of {n1} and {n2} liters. The objective is to collect exactly {n3} liters of water, using a large water reservoir.

Each step of the game offers you the choice to execute one of two actions:

Opt for a bottle and proceed to fill it to its brim from the reservoir or conversely, empty it completely back into the reservoir. The following are some illustrative examples:
[0 / 7, 7 / 22] -> (fill the first) [7 / 7, 7 / 22];
[8 / 8, 11 / 19] -> (empty the first) [0 / 8, 11 / 19].

Pour water from one bottle into the other. This action concludes once the recipient bottle is at its full capacity or the source bottle is entirely empty. Here are some practical examples:
[0 / 7, 9 / 9] -> (pour the second to the first, it will halt by the full recipient) [7 / 7, 2 / 9];
[5 / 5, 5 / 7] -> (pour the first to the second, it will halt by the full recipient) [3 / 5, 7 / 7];
[12 / 12, 0 / 17] -> (pour the first to the second, it will halt by the empty source) [0 / 12, 12 / 17];

Now you are facing a subtask of this game. Given a state, estimate how many steps to reach the goal {n3}.
The state now is {input}.
(Your response should be an integer. Do not contain any other things in your response!)'''

class TASKDropWater(TASK):
    def __init__(self):
        super().__init__()
        self.name = 'DropWater'
    
    def get_steps(self, line):
        n1, n2, n3, n4 = line.split()
        return int(n4)
    
    def prompt_input(self, line):
        n1, n2, n3, n4 = line.split()
        return f'''This game involves two empty bottles with capacities of {n1} and {n2} liters. The objective is to collect exactly {n3} liters of water in either bottle within {n4} steps, using a large water reservoir.

Each step of the game offers you the choice to execute one of two actions:

Opt for a bottle and proceed to fill it to its brim from the reservoir or conversely, empty it completely back into the reservoir. The following are some illustrative examples:
[0 / 7, 7 / 22] -> (fill the first) [7 / 7, 7 / 22];
[8 / 8, 11 / 19] -> (empty the first) [0 / 8, 11 / 19].

Pour water from one bottle into the other. This action concludes once the recipient bottle is at its full capacity or the source bottle is entirely empty. Here are some practical examples:
[0 / 7, 9 / 9] -> (pour the second to the first, it will halt by the full recipient) [7 / 7, 2 / 9];
[5 / 5, 5 / 7] -> (pour the first to the second, it will halt by the full recipient) [3 / 5, 7 / 7];
[12 / 12, 0 / 17] -> (pour the first to the second, it will halt by the empty source) [0 / 12, 12 / 17];

Please solve this problem step by step.
Remember you need to have a summary in the last line of your reply: [0 / X, 0 / Y] -> [x1 / X, y1 / Y] -> [x2 / X, y2 / Y] -> ... -> [xk / X, yk / Y] (one of xk and yk is {n3}, since the goal is {n3})
For example, 2 steps to get 3 using 6 and 9, the last line of your response may be: [0 / 6, 0 / 9] -> [0 / 6, 9 / 9] -> [6 / 6, 3 / 9]
'''
    
    def check_conclu(self, line, conclusion):
        n1, n2, n3, n4 = line.split()
        n1, n2, n3, n4 = int(n1), int(n2), int(n3), int(n4)
        try:
            washed = ''
            cnt = 0
            for char in conclusion:
                if char == '[':
                    cnt += 1
                if cnt>0:
                    washed += char
                if char == ']':
                    cnt -= 1
            numbers = extract(washed)
            if len(numbers) > (n4 + 1) * 4: return 0
            if len(numbers) < 8: return 0
            if diff(numbers[0], 0) or diff(numbers[2], 0): return 0
            if diff(numbers[-2], n3) and diff(numbers[-4], n3): return 0
            def drop(op, x, y, a, b):
                if op=='fill_a': return a, y
                if op=='fill_b': return x, b
                if op=='empty_a': return 0, y
                if op=='empty_b': return x, 0
                if op=='a_to_b':
                    t = min(x, b-y)
                    return x-t, y+t
                if op=='b_to_a':
                    t = min(y, a-x)
                    return x+t, y-t
            for i in range(4, len(numbers)-2, 4):
                a1, a2 = numbers[i-4], numbers[i-2]
                b1, b2 = numbers[i], numbers[i+2]
                correct = False
                for op in ['fill_a', 'fill_b', 'empty_a', 'empty_b', 'a_to_b', 'b_to_a']:
                    c1, c2 = drop(op, a1, a2, n1, n2)
                    if diff(b1, c1) == False and diff(b2, c2) == False:
                        correct = True
                if correct == False:
                    return 0
        except:
            return 0
        return 1
    
    def wash_out(self, out):
        if out.count('->') <= 4 and max([o.count('->') for o in out.split('\n')]) <= 1:
            lines = out.split('\n')
            res = lines[0]
            for li in lines[1:]:
                res += ' ' + li[li.find('->'):]
            return res
        else:
            return out
    
    def propose_prompt_wrap(self, x: str, y: str='') -> str:
        n1, n2, n3, n4 = x.split()
        current_numbers = get_current_numbers(x, y)
        a, b, c, d = current_numbers
        prompt = (propose_prompt if self.shot>0 else propose_prompt_zero_shot).format(input=f'[{a} / {b}, {c} / {d}]', n1=n1, n2=n2, n3=n3, n4=n4)
        return prompt
    
    def value_prompt_wrap(self, x: str, y: str) -> str:
        current_numbers = get_current_numbers(x, y)
        n1, n2, n3, n4 = x.split()
        a, b, c, d = current_numbers
        return (value_prompt if self.shot>0 else value_prompt_zero_shot).format(input=f'[{a} / {b}, {c} / {d}]', n1=n1, n2=n2, n3=n3, n4=n4)
    
    def value_outputs_unwrap(self, x: str, y: str, value_outputs: list) -> float:
        value = - sum([abs(float(n)) for n in re.findall(r'[-+]?[0-9]*\.?[0-9]+', x)][-1] for x in value_outputs)/len(value_outputs)
        return value