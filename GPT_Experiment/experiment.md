## Environment Setup

- Set your `OPENAI_API_KEY`.
- `pip install fire`

## Run

- `python run.py -task='DropWater' -group='nct' -split='valid' -shot=0 -consistency=1 -tot_width=5`
- `task`: one of DropWater, NumPath, NumSplit, or threetoN
- `group`: `nct` for ATS-BFS, `dfs` for ATS-DFS, `cot` for CoT, `tot` for ToT
- `split`: one of train or valid
- `shot`: 0/1/2/3/4
- (width is ignored for all except ToT)

## Evaluate

- `python check.py -task='threetoN' -group='nct' -shot=0 -consistency=1 -width=1`
- (width is ignored for all except ToT)

