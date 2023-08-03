batch_dir=data/gpt3_generations/

python3 self_instruct/self_background_gpt.py \
    --batch_dir ${batch_dir} \
    --num_instructions_to_generate 20 \
    --seed_tasks_path data/gpt3_seeds.json \
    --engine_chat "gpt-3.5-turbo" \
    --engine_new "davinci" \
    --api_key "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"
