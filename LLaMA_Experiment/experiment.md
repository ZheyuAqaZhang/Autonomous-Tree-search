## Environment Setup

```
torch==1.13.1
transformers==4.27.1
```

## Data Preparation

- A folder with x.in and x.out.
- e.g. `data/trainset/{task}/{split}/{instance_id}.in`

## Fine-tune

- Make sure `NUM_GPU` (in run.sh) is correct.
- `bash run.sh "--task=DropWater --modelname=eachadea/vicuna-13b-1.1" [Experiment Directory]`
- `--task=`: one of DropWater, NumPath, NumSplit, or threetoN
- `--modelname=`: huggingface model name
- `[Experiment Directory]`: where to save checkpoints

## Generate

- `python generate.py --task=NumPath --modelname=cache/downloaded_llama7B --checkpoint=xxx.pt`
- The generated output are in the folder of the checkpoint.