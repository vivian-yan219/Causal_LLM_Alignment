batch_dir=data/gpt3_generations/

python3 self_instruct/generate_instances.py \
    --batch_dir ${batch_dir} \
    --input_file machine_generated_instructions.json \
    --output_file machine_generated_instances.json \
    --max_instances_to_gen 5 \
    --engine "gpt-3.5-turbo" \
    --request_batch_size 5 \
    --api_key "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"

