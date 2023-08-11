batch_dir=data/gpt3_generations/

python3 self_instruct/self_background_gpt.py \
    --batch_dir ${batch_dir} \
    --num_instructions_to_generate 20 \
    --seed_tasks_path data/gpt3_seeds.json \
    --engine_chat "gpt-3.5-turbo" \
    --engine_new "davinci" \
<<<<<<< HEAD
    --api_key "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"
=======
    --api_key ""
>>>>>>> 369747b0deb8b3906b64c9762cbcd6191b4e19dd
