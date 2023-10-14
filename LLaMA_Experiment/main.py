print('start main')

import torch, functools, transformers, os
import torch.nn as nn
import torch.distributed as dist
from transformers import AutoModelForCausalLM, AutoTokenizer
from torch.distributed.fsdp import (
    FullyShardedDataParallel as FSDP,
    MixedPrecision,
)
from fairscale.nn.checkpoint.checkpoint_activations import checkpoint_wrapper

from utils import gpu_memory_usage, save_checkpoint, load_checkpoint, lora_model
from torch.distributed.fsdp.wrap import transformer_auto_wrap_policy
from data.get_data import get_dataset
from torch.utils.data.dataloader import DataLoader
from torch.utils.data.distributed import DistributedSampler
from torch.distributed.fsdp.sharded_grad_scaler import ShardedGradScaler


# init

import argparse

parser = argparse.ArgumentParser(description='')

parser.add_argument('--task', type=str, default="3to24")
parser.add_argument('--split', type=str, default="ours")
parser.add_argument('--outputdir', type=str)
parser.add_argument('--modelname', type=str, default="")
config = parser.parse_args()
print(config)


import os
if os.path.exists(os.path.join(config.outputdir, 'iter_250.pt')):
    exit(0)

dist.init_process_group("nccl")
rank = dist.get_rank()
device_id = rank % torch.cuda.device_count()
world_size = torch.distributed.get_world_size()
torch.cuda.set_device(device_id)

model_name = config.modelname

# tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir='./cache')
tokenizer = AutoTokenizer.from_pretrained(model_name)


dist.barrier()
if rank == 0: dataset = get_dataset(config.task, model_name, 3000, split=config.split)
dist.barrier()
if rank != 0: dataset = get_dataset(config.task, model_name, 3000, split=config.split)
dist.barrier()


# model = AutoModelForCausalLM.from_pretrained(model_name, cache_dir='./cache')
model = AutoModelForCausalLM.from_pretrained(model_name)


for i in range(len(model.model.layers)):
    model.model.layers[i] = checkpoint_wrapper(model.model.layers[i])

model = FSDP(model,
            device_id=torch.cuda.current_device(),
            mixed_precision=MixedPrecision(param_dtype=torch.float16,reduce_dtype=torch.float16,buffer_dtype=torch.float16),
            auto_wrap_policy=functools.partial(
                transformer_auto_wrap_policy,
                transformer_layer_cls={transformers.models.llama.modeling_llama.LlamaDecoderLayer},
            )
        )

optimizer = torch.optim.AdamW(model.parameters(), lr=1e-5)

dist.barrier()

# train

train_loader = DataLoader(
    dataset,
    sampler=DistributedSampler(dataset, shuffle=True, drop_last=False),
    batch_size=1,
)

iter_num = 0
loss_fn = nn.CrossEntropyLoss(ignore_index=-1)
scaler = ShardedGradScaler()
acc_steps = 10
model.train()

while iter_num <= 250:
    data_iter = iter(train_loader)
    while True:
        try:
            batch = next(data_iter)
        except:
            break
        token_ids = torch.stack([torch.cat(o, dim=0) for o in batch['input_ids']], dim=0).to(device_id)
        x = token_ids[:, :-1]
        y = token_ids[:, 1:]
        logits = model(torch.max(x,torch.tensor(0))).logits
        loss = loss_fn(logits.reshape(-1, logits.shape[-1]), y.reshape(-1))
        
        scaler.scale(loss / acc_steps).backward()
        if iter_num == 0: optimizer.zero_grad()
        
        iter_num += 1
        if iter_num % acc_steps == 0:
            scaler.unscale_(optimizer)
            scaler.step(optimizer)
            scaler.update()
            optimizer.zero_grad()
            model.zero_grad(set_to_none=True)
        
        dist.all_reduce(loss, op=dist.ReduceOp.SUM)
        loss = loss / world_size
        if rank == 0:
            print(f'iter {iter_num},  loss {loss.item()}')
            print(gpu_memory_usage())
        
        if iter_num % 125 == 0:
            os.makedirs(config.outputdir, exist_ok=True)
            save_checkpoint(rank, config.outputdir, iter_num, model, optimizer)
            goal_name = f"iter_{iter_num}.pt"
            if rank == 0:
                os.system(f'cp {os.path.join(config.outputdir, "latest.pt")} {os.path.join(config.outputdir, goal_name)}')
            dist.barrier()
