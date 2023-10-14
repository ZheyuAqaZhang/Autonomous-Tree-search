from utils import *
import re, traceback

def get_current_ints(y: str) -> int:
    last_line = y.strip().split('\n')[-1]
    res = extract(last_line)
    return [int(x) for x in res]

# 2-shot
propose_prompt = '''Given two variables A, B, and a list of numbers. You need to factorize the first number in the list as x*y, and add the two factors to the two variables respectively (namely, A+=x, B+=y), and then erase the first number from the list.
Input: A=2, B=3, numbers: 6 3
Possible next steps:
(6=1*6) -> A=3, B=9, numbers: 3
(6=2*3) -> A=4, B=6, numbers: 3
(6=3*2) -> A=5, B=5, numbers: 3
(6=6*1) -> A=8, B=4, numbers: 3
Input: A=18, B=4, numbers: 5
Possible next steps:
(5=1*5) -> A=19, B=9, numbers: 
(5=5*1) -> A=23, B=5, numbers: 
Input: {input}
Possible next steps:
'''

# Given the input information about the value of A, B, and the list of numbers, you should factorize and then delete the first number in the list as x*y to add A by x and add B by y. 
propose_prompt_zero_shot = '''Given two variables A, B, and a list of numbers. You need to factorize the first number in the list as x*y, and add the two factors to the two variables respectively (namely, A+=x, B+=y), and then erase the first number from the list.
Input: {input}
Since there are multiple possibilities, your answer should span multiple lines, where each line is a distinct solution. Suppose the input is 
A=_, B=_, numbers: u ___, 
you should maintain this format
(u=x*y) -> A=_, B=_, numbers: ___
Note that u must be the first number in the list. For the second and the third number (if exists), maintain them in your response.
Note that "()" encloses a factorization, and the next status should be after "->".
Do not contain any other things in your response!
'''

# 2-shot
summary_prompt = '''Given two variables A, B, and a list of numbers. You need to factorize the first number in the list as x*y, and add the two factors to the two variables respectively (namely, A+=x, B+=y), and then erase the first number from the list. Now you have decided all the numbers in the list, and you need to answer the value of A*B.
Input: (5=5*1) -> A=23, B=5, numbers: 
Answer = 23 * 5 = 115
Input: (6=3*2) -> A=18, B=4, numbers: 
Answer = 18 * 4 = 72
Input: {input}
Answer = '''

summary_prompt_zero_shot = '''Given two variables A, B, and a list of numbers. You need to factorize the first number in the list as x*y, and add the two factors to the two variables respectively (namely, A+=x, B+=y), and then erase the first number from the list. Now you have decided all the numbers in the list, and you need to answer the value of A*B. 
Input: {input}
Your answer should follow this format:
A * B = C 
(e.g. 4 * 18 = 72) Do not contain any other things in your response!'''

# 4-shot
value_prompt = '''Given two variables A, B, and some numbers, you need to factorize the first number and add each one factor to one variable. After considering all numbers, you need to minimize A*B. Estimate how small the final result can be. You can try a few lookahead simulations to do so. Exceptionally, if the answer is given, then your estimation should be equal to that answer.
input: A=3, B=9, numbers: 3
3=1*3, A=4, B=12 //A*B=48
3=3*1, A=6, B=10 //A*B=60
output: 48
input: A=4, B=2, numbers: 4 3
4=2*2, 3=3*1, A=9, B=5 //A*B=45
4=4*1, 3=1*3, A=9, B=6 //A*B=54
output: 45
input: A=4, B=2, numbers: 
the final scenario is unique
output: 8
input: Answer = 18 * 4 = 72
output: 72
input: {input}
'''

value_prompt_zero_shot = '''Given two variables A, B, and a list of numbers. You need to factorize each number in the list as x*y, and add the two factors to the two variables respectively (namely, A+=x, B+=y). Your goal is to minimize A*B. Estimate how small the final result can be.
input: {input}
Your answer should consist of only one number. Do not contain any other things in your response!
'''

value_prompt_zero_shot_2 = '''Given two variables A, B, you should output the product A*B. The input format could be either A=x, B=y or A * B = C. In the second case, it's okay to directly output C.
input: {input}
Your answer should consist of only one number. Do not contain any other things in your response!
'''

class TASKNumSplit(TASK):
    def __init__(self):
        super().__init__()
        self.name = 'NumSplit'
        self.steps = 4
    
    def prompt_input(self, line):
        return f'''You are given three numbers: {line.replace(' ',', ')}, and initially there are two variables X=0 and Y=0. You should write each number as a product x*y, then add x to X and add y to Y. Finally, your goal is to minimize X*Y.
        
To tackle this problem, you should consider the three numbers one by one (consider the i-th number in the i-th step). In each step, you can choose how to write the number as a product x*y. We use [X,Y] to represent a current state, and you can update the state after knowing x and y. For example, if this number is 12, then the following options are some illustrative examples for this step:
[5,7] -> (12=4*3) [9,10]
[8,4] -> (12=2*6) [10,10]
[2,5] -> (12=6*2) [8,7]

Finally, after considering all the numbers, you must perform another operation to calculate X*Y. For example:
[9,10] -> 90
[8,7] -> 56

The goal is to minimize X*Y in the end. Please solve this problem step by step. Remember you need to have a summary in the last line of your reply: ans=x, where x represents the final answer.

For example:
Given input 1,6,2, your summary should be ans=24.
'''
    
    def check_conclu(self, line, conclusion):
        # print('conclusion', conclusion)
        n1, n2, n3 = line.split()
        n1, n2, n3 = int(n1), int(n2), int(n3)
        res = extract(conclusion)[-1]
        mn = 1e10
        for x in range(1,n1+1):
            for y in range(1,n2+1):
                for z in range(1,n3+1):
                    if n1%x==0 and n2%y==0 and n3%z==0 and mn>(x+y+z)*(n1//x+n2//y+n3//z):
                        mn = (x+y+z)*(n1//x+n2//y+n3//z)
        if res != mn: return 0
        return 1

    def get_state_from_y(self, y: str='') -> str:
        y = y.strip().split('\n')[-1]
        p = max(y.find('A'),0)
        y = y[p:]
        p = y.find('numbers')
        flag = sum([c.isdigit() for c in y[p:]])
        if flag==0:
            y = y[:p-2]
        # print('test',y)
        return y

    def wash_out(self, out):
        # return out
        is_tot = True
        for i in range(3):
            this = out.split('\n')[i]
            if out.count('->') != 1 or out.count('numbers:') != 1:
                is_tot = False
        if is_tot:
            return 'ans:' + out.split('\n')[3]
        else:
            return out
    
    def propose_prompt_wrap(self, x: str, y: str='') -> str:
        if not y:
            cur = f'A=0, B=0, numbers: {x}'
        else:
            cur = self.get_state_from_y(y)
        # print('propose_prompt_wrap', cur)
        if 'numbers:' in cur:
            prompt = (propose_prompt if self.shot>0 else propose_prompt_zero_shot).format(input=cur)
        else:
            prompt = (summary_prompt if self.shot>0 else summary_prompt_zero_shot).format(input=cur)
        return prompt

    def value_prompt_wrap(self, x: str, y: str) -> str:
        cur = self.get_state_from_y(y)
        # print('value_prompt_wrap:','{'+y+'}','{'+cur+'}')
        return (value_prompt if self.shot>0 else (value_prompt_zero_shot if ('numbers' in cur) else value_prompt_zero_shot_2)).format(input=cur)
    
    def value_outputs_unwrap(self, x: str, y: str, value_outputs: list) -> float:
        try:
            value = -sum([abs(float(n)) for n in re.findall(r'[-+]?[0-9]*\.?[0-9]+', x)][-1] for x in value_outputs)/len(value_outputs) # larger is better
            return value
        except:
            print(traceback.format_exc())
            return 0