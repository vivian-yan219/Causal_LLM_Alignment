batch_dir=data/gpt3_generations/

python3 self_instruct/bootstrap_instructions.py \
    --batch_dir ${batch_dir} \
    --num_instructions_to_generate 5 \
    --seed_tasks_path data/seed_tasks.jsonl \
    --engine "davinci" \
    --api_key "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"
