from transformers import AutoTokenizer, AutoModelForCausalLM
import transformers
import torch, os


import argparse
parser = argparse.ArgumentParser(description='')
parser.add_argument('--task', type=str, default="all")
parser.add_argument('--checkpoint', type=str)
parser.add_argument('--modelname', type=str, default="")
parser.add_argument('--dosample', type=int, default=1)
config = parser.parse_args()

task = config.task
model_name = config.modelname
checkpoint_path = config.checkpoint
method = checkpoint_path[checkpoint_path.find('llama'):checkpoint_path.rfind('/')]
print('method=',method)

if not os.path.exists(checkpoint_path):
    print('skip',method)
    exit(0)

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

if 'iter_0.pt' not in checkpoint_path:
    checkpoint = torch.load(checkpoint_path, map_location='cpu')
    full_state_dict = checkpoint['model_state_dict']
    new_full_state_dict = {x:full_state_dict[x] for x in full_state_dict if 'inv_freq' not in x}
    model.load_state_dict(new_full_state_dict)
    del checkpoint
    torch.cuda.empty_cache()

cache_path = f'./temp/{task}_{method}'
model.save_pretrained(cache_path)
model = AutoModelForCausalLM.from_pretrained(
    cache_path, device_map="auto"
)
import random, copy
def randomed(lst):
    lst = copy.deepcopy(lst)
    random.shuffle(lst)
    return lst



output_path = f'tasks/{task}/output/{method}/valid'
os.makedirs(output_path, exist_ok=True)

if task in ['threetoN', 'NumPath', 'DropWater', 'NumSplit']:
    for i in randomed([xxx for xxx in range(100)]):
        if os.path.exists(f'{output_path}/{i}.out'): continue
        if not os.path.exists(f'NCT/tasks/{task}/output/cot_0shot_1cons/valid/{i}.in'): continue
        
        ipt = open(f'NCT/tasks/{task}/output/cot_0shot_1cons/valid/{i}.in', 'r').read()
        prompt = f'''# Question\n{ipt}\n\n# Answer\n'''
        print('data',i,'begin generating',len(ipt))

        outputs = model.generate(**tokenizer(prompt, return_tensors="pt").to("cuda"),
                            max_new_tokens=(1588 if method=='cot' else 3588),
                            do_sample=True, #(True if config.dosample else False),
                            temperature=0.2,
                            top_k=0,
                            num_return_sequences=1,
                            eos_token_id=tokenizer.eos_token_id)

        # print(tokenizer.decode(outputs[0], skip_special_tokens=True))
        print('data',i,'finish generating')
        
        open(f'{output_path}/{i}.in', 'w').write(ipt)
        open(f'{output_path}/{i}.out', 'w').write(tokenizer.decode(outputs[0], skip_special_tokens=True))
