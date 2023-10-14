export OMP_NUM_THREADS=4

export WORLD_SIZE=$(scontrol show hostnames "$SLURM_JOB_NODELIST" | wc -l)
export MASTER_ADDR=$(scontrol show hostnames "$SLURM_JOB_NODELIST" | head -n 1)
export MASTER_PORT=51234

DEFAILT_EXP=test_$( date +%Y-%m-%d_%H-%M-%S )
EXP_NAME=${2:-$DEFAILT_EXP}

OUTPUT_DIR=checkpoints/$EXP_NAME

echo $OUTPUT_DIR
if [ ! -d "$OUTPUT_DIR" ]; then
    mkdir -p "$OUTPUT_DIR"
    echo "Path created: $OUTPUT_DIR"
else
    echo "Path already exists: $OUTPUT_DIR"
fi

NUM_GPU=4
ELSE_ARGS=${1:-''}

torchrun \
    --nproc_per_node=$NUM_GPU \
    --nnodes=$WORLD_SIZE:$WORLD_SIZE \
    --rdzv_id=${EXP_NAME} \
    --rdzv_backend=c10d \
    --rdzv_endpoint=$MASTER_ADDR:$((MASTER_PORT+1)) \
    --max_restarts=3 \
    main.py --outputdir=${OUTPUT_DIR} ${ELSE_ARGS} # >${OUTPUT_DIR}/log
