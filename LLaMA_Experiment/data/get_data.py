from datasets import Dataset
import os, json, torch, random

'''
split in 'cot_train', 'nct_train', 'tot_1width_train', 'tot_tree_train', 'tot_5width_train', 'tot_tree_2width_train', 'dfs_train'
'''
def get_dataset(name, model_name, max_tokens, split='ours'):
    cache_name = model_name.rstrip('/')
    cache_name = cache_name[cache_name.rfind('/')+1:]
    cache_dir = f'cache/{name}_{cache_name}_{max_tokens}_{split}'
    print(cache_dir)
    from transformers import AutoTokenizer
    # tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir='./cache')
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    if name in ['threetoN', 'NumPath', 'NumSplit', 'DropWater']:
        cannot_load = False
        try:
            Dataset.load_from_disk(cache_dir)
            return dataset
        except:
            cannot_load = True
        
        if not os.path.exists(cache_dir) or cannot_load:
            token_ids = []
            for instance_id in range(1000):
                try:
                    ipt = open(f'data/trainset/{name}/{split}/{instance_id}.in', 'r').read()
                    opt = open(f'data/trainset/{name}/{split}/{instance_id}.out', 'r').read()
                    txt = f'''# Question\n{ipt}\n\n# Answer\n{opt}'''
                    s = tokenizer.encode(txt, truncation=False, return_tensors="pt")[0]
                    t = torch.zeros((s.shape[0]+1), dtype=torch.long)
                    t[:-1] = s
                    t[-1] = tokenizer.eos_token_id
                    s = t
                    # print(instance_id, len(s))
                    if len(s) < 2888:
                        token_ids.append(s)
                except:
                    pass
            
            random.seed(12345)
            random.shuffle(token_ids)
            
            batched_ids = []
            i, j = 0, 0
            while i<len(token_ids):
                j = i
                if j<len(token_ids):  # changed from `while` to `if`. ensure one instance !!!
                    ts = torch.nn.utils.rnn.pad_sequence(token_ids[i:j+1], batch_first=True, padding_value=-1)
                    if ts.shape[0]*ts.shape[1] > max_tokens: break
                    j += 1
                if i==j:
                    i+=1
                    continue
                ts = torch.nn.utils.rnn.pad_sequence(token_ids[i:j], batch_first=True, padding_value=-1)
                # print(i,j)
                batched_ids.append(ts)
                i = j
            dataset = Dataset.from_dict({'input_ids': batched_ids})
            dataset.save_to_disk(cache_dir)
            return dataset
        
        dataset = Dataset.load_from_disk(cache_dir)
        print(dataset)
        return dataset
    
    assert 0

if __name__=='__main__':
    for name in ['threetoN', 'NumPath', 'NumSplit', 'DropWater']:
        for split in ['cot_train', 'nct_train', 'tot_1width_train', 'tot_tree_train', 'tot_5width_train', 'tot_tree_2width_train', 'dfs_train']:
            get_dataset(name, "cache/downloaded_llama13B", 3000, split)