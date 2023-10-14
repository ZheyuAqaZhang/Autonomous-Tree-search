import fire, random, os, shutil, openai, concurrent, time
from utils import get_task, prompt_global, call_gpt
import itertools
import numpy as np
import json, traceback

def gpt(env, prompt, model="gpt-4-0613", temperature=0.7, max_tokens=1000, n=1, stop=None) -> list: # for tot
    messages = [{"role": "user", "content": prompt}]
    while True:
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                n=n,
                request_timeout=600,
            )
            env.completion_tokens += response["usage"]["completion_tokens"]
            env.prompt_tokens += response["usage"]["prompt_tokens"]
            return [choice["message"]["content"] for choice in response["choices"]]
        except:
            print(traceback.format_exc())
            time.sleep(10)

def get_value(env, x, y, n_evaluate_sample, cache_value=True):
    value_prompt = env.value_prompt_wrap(x, y)
    if cache_value and value_prompt in env.value_cache:
        return env.value_cache[value_prompt]
    value_outputs = gpt(env, value_prompt, n=n_evaluate_sample, stop=None)
    value = env.value_outputs_unwrap(x, y, value_outputs)
    if cache_value:
        env.value_cache[value_prompt] = value
    return value

def get_values(env, x, ys, n_evaluate_sample, cache_value=True):
    values = []
    local_value_cache = {}
    for y in ys:  # each partial output
        if y in local_value_cache:  # avoid duplicate candidates
            value = 0
        else:    
            value = get_value(env, x, y, n_evaluate_sample, cache_value=cache_value)
            local_value_cache[y] = value
        values.append(value)
    return values

def get_proposals(env, x, y): # for tot
    propose_prompt = env.propose_prompt_wrap(x, y)
    proposals = gpt(env, propose_prompt, n=1, stop=None)[0].split('\n')
    return [y + _ + '\n' for _ in proposals]

def run_an_instance(task, group, split, i, line, shot, consistency, tot_width):
    try:
        print(task, group, split, i, '['+line+']', shot, consistency, tot_width)
        env = get_task(task)
        env.shot = shot
        
        if group == 'tot':
            output_dir = f'tasks/{task}/output/{group}_{shot}shot_{consistency}cons_{tot_width}width/{split}'
        else:
            output_dir = f'tasks/{task}/output/{group}_{shot}shot_{consistency}cons/{split}'
        
        os.makedirs(output_dir, exist_ok=True)
        if group == 'tot':
            assert split == 'valid'
            if os.path.exists(f'{output_dir}/{i}.out'):
                return
            x = line
            ys = ['']  # current output candidates
            infos = []
            for step in range(env.get_steps(line)):
                # generation
                new_ys = [get_proposals(env, x, y) for y in ys]
                new_ys = list(itertools.chain(*new_ys))
                print(x, new_ys)
                ids = list(range(len(new_ys)))
                # evaluation
                values = get_values(env, x, new_ys, consistency)
                print(values)
                # selection
                select_ids = sorted(ids, key=lambda x: values[x], reverse=True)[:tot_width]
                select_new_ys = [new_ys[select_id] for select_id in select_ids]
                
                infos.append({'step': step, 'x': x, 'ys': ys, 'new_ys': new_ys, 'values': values, 'select_new_ys': select_new_ys})
                ys = select_new_ys
            
            with open(f'{output_dir}/{i}.json', 'w') as f:
                json.dump(infos, f, indent=4)

            for T, y in enumerate(ys):
                open(f'{output_dir}/{i}_{T}.out', 'w').write(y)
            res = ys[0]
            for y in ys:
                # if env.check_conclu(x, y):
                if env.check(x, y):
                    res = y
            open(f'{output_dir}/{i}.out', 'w').write(res)
            usage_prompt, usage_generate = env.prompt_tokens, env.completion_tokens
            open(f'{output_dir}/{i}.log', 'w').write(f'{usage_prompt} {usage_generate}')
        
        if group == 'cot' or group == 'nct':
            if not os.path.exists(f'{output_dir}/{i}.in'):
                open(f'{output_dir}/{i}.in', 'w').write(env.prompt_input(line))
            messages = [
                {"role": "system", "content": prompt_global()},
                {"role": "user", "content": env.prompt_input(line)},
            ]
            if group == 'cot':
                messages = messages[1:]
            if shot >= 1:
                messages = messages[:-1] + env.prompt_few_shot(group, shot) + messages[-1:]
            if not os.path.exists(f'{output_dir}/{i}.out'):
                res_list, usage_prompt, usage_generate = call_gpt(messages, consistency)
                open(f'{output_dir}/{i}.log', 'w').write(f'{usage_prompt} {usage_generate}')
                for T in range(consistency):
                    open(f'{output_dir}/{i}_{T}.out', 'w').write(res_list[T])
                for T in range(consistency):
                    if env.check(line, res_list[T]) or (T==consistency-1 and split=='valid'):
                        shutil.copy2(f'{output_dir}/{i}_{T}.out', f'{output_dir}/{i}.out')
                        break
    except:
        print(traceback.format_exc())

def run(task='GraphGame', group='nct', split='valid', shot=0, consistency=1, tot_width=5):
    data = open(f'tasks/{task}/data/{split}.txt', 'r')
    
    ex = concurrent.futures.ProcessPoolExecutor(10)
    
    for i, line in enumerate(data):
        line = line.strip('\n')
        if len(line) < 2: continue
        ex.submit(run_an_instance, task, group, split, i, line, shot, consistency, tot_width)
        # run_an_instance(task, group, split, i, line, shot, consistency, tot_width)
    
    ex.shutdown(wait=True)
    
    return

if __name__ == '__main__':
    fire.Fire(run)
