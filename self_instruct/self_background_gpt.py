import os
import json
import random
import re
import string
import tqdm
import argparse
import numpy as np
import pandas as pd
from multiprocessing import Pool
from functools import partial
from rouge_score import rouge_scorer
from gpt3_api import make_requests as make_gpt3_requests_generate_new
from gpt3_api import make_gpt3_requests_chat


random.seed(5)


def encode_prompt(prompt_instructions, classification=False):
    """Encode multiple prompt instructions into a single string."""
    if classification:
        prompt = "Come up with a series of classification tasks. Try to specify the possible output labels when possible.\n"
    else:
        prompt = "Come up with a series of causal graphs:\n"
    
    for idx, instruction in enumerate(prompt_instructions):
        instruction = re.sub(r"\s+", " ", instruction).strip().rstrip(":")
        prompt += f"{idx+1}. {instruction}\n"
    prompt += f"{len(prompt_instructions) + 1}."
    return prompt


def sample_machine_instructions(machine_instructions, n):
    """Sample n machine instructions from a list of machine instructions."""
    return random.sample(machine_instructions, min(n, len(machine_instructions)))


def find_word_in_string(w, s):
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search(s)


def post_process_gpt3_response(response):
    if response is None or response["choices"][0]["finish_reason"] == "length":
        return []
    raw_instructions = re.split(r"\n\d+\s?\. ", response["choices"][0]["text"])
    instructions = []
    for inst in raw_instructions:
        inst = re.sub(r"\s+", " ", inst).strip()
        inst = inst.strip().capitalize()
        if inst == "":
            continue
        # filter out too short or too long instructions
        if len(inst.split()) <= 3 or len(inst.split()) > 150:
            continue
        # filter based on keywords that are not suitable for language models.
        if any(find_word_in_string(word, inst) for word in ["image", "images", "graph", "graphs", "picture", "pictures", "file", "files", "map", "maps", "draw", "plot", "go to"]):
            continue
        # We found that the model tends to add "write a program" to some existing instructions, which lead to a lot of such instructions.
        # And it's a bit comfusing whether the model need to write a program or directly output the result. 
        # Here we filter them out.
        # Note this is not a comprehensive filtering for all programming instructions.
        if inst.startswith("Write a program"):
            continue
        # filter those starting with punctuation
        if inst[0] in string.punctuation:
            continue
        # filter those starting with non-english character
        if not inst[0].isascii():
            continue
        instructions.append(inst)
    return instructions


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--batch_dir",
        type=str,
        required=True,
        default="data/gpt3_generations/",
        help="The directory where the batch is stored.",
    )
    parser.add_argument(
        "--seed_tasks_path",
        type=str,
        required=True,
        default="data/seed_tasks.jsonl",
        help="The path to the human written data.",
    )
    parser.add_argument(
        "--num_instructions_to_generate",
        type=int,
        default=5,
        help="th",
    )
    parser.add_argument(
        "--use_clf_seed_tasks_only",
        action="store_true",
        help="If specified, we will only use the classification seed tasks to prompt new instructions. This will lead to more classification instructions.",
    )
    parser.add_argument(
        "--engine_chat",
        type=str,
        default="gpt-3.5-turbo",
        help="The engine to use to expand the graph."
    )
    parser.add_argument(
        "--engine_new",
        type=str,
        default="davinci",
        help="The engine to use to generate new prompts."
    )
    parser.add_argument(
        "--num_prompt_instructions",
        type=int,
        default=5,
        help="The number of instructions to use in the prompt."
    )
    parser.add_argument(
        "--request_batch_size",
        type=int,
        default=3,
        help="The number of requests to send to GPT3 at a time."
    )
    parser.add_argument(
        "--api_key",
        type=str,
        help="The API key to use. If not specified, the key will be read from the environment variable OPENAI_API_KEY."
    )
    parser.add_argument(
        "--organization",
        type=str,
        help="The organization to use. If not specified, the default organization id will be used."
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    seed_tasks = [task for task in json.loads(open(args.seed_tasks_path, 'r').read())]
    if args.use_clf_seed_tasks_only:
        seed_tasks = [t for t in seed_tasks if t["is_classification"]]
    seed_instructions = [t["background"] for t in seed_tasks]
    print(f"Loaded {len(seed_instructions)} human-written seed instructions")
    
    os.makedirs(args.batch_dir, exist_ok=True)
    # load the LM-generated instructions
    machine_instructions = []
    request_idx = 0
    if os.path.exists(os.path.join(args.batch_dir, 'machine_generated_instructions.json')):
        with open(os.path.join(args.batch_dir, 'machine_generated_instructions.json'), 'r')as fin:
            for line in fin:
                instruction_info = json.loads(line)
                machine_instructions.append(instruction_info['instruction'])
                request_idx = instruction_info['request_idx'] + 1
        print(f'Loaded {len(machine_instructions)} machine-generated instructions')

    # similarities = {}
    scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=False)

    # generate new instructions
    progress_bar = tqdm.tqdm(total=args.num_instructions_to_generate)
    if machine_instructions:
        progress_bar.update(len(machine_instructions))

    expanded_prompts = open(("data/gpt3_generations/expanded_prompts.json"), "w")
    
    with open(os.path.join(args.batch_dir, "machine_generated_instructions.json"), "a") as fout:
        while len(machine_instructions) < args.num_instructions_to_generate:
            
            # batch size: 分批创建batch input，从中归纳graph in json
            batch_inputs = []
            for _ in range(args.request_batch_size):
                # sample machine instructions from the pool
                prompt_instructions = sample_machine_instructions(
                    machine_instructions, 
                    n=2)
                # sample human instructions from the pool
                # 填充machine不够的，但在一开始machine还没generate的时候，需要剔除已经方进来的，不然会重复
                prompt_instructions += random.sample(seed_instructions, args.num_prompt_instructions - len(prompt_instructions))
                
                random.shuffle(prompt_instructions)
                
                prompt = encode_prompt(prompt_instructions, classification=args.use_clf_seed_tasks_only)       
                batch_inputs.append(prompt)
            print(len(batch_inputs))

            results = make_gpt3_requests_generate_new(
                engine=args.engine_new,
                prompts=batch_inputs,
                max_tokens=1024,
                temperature=0.7,
                top_p=0.5,
                frequency_penalty=0,
                presence_penalty=2,
                stop_sequences=["\n\n", "\n16", "16.", "16 ."],
                logprobs=1,
                n=1,
                best_of=1,
                api_key=args.api_key,
                organization=args.organization,
            )

            instructions = []
            all_metadata = []
            for result in results:
                new_instructions = post_process_gpt3_response(result["response"])
                instructions += new_instructions
                all_metadata += [result] * len(new_instructions)

            for inst, metadata in zip(instructions, all_metadata):
                with Pool(4) as p:
                    rouge_scores = p.map(partial(scorer.score, inst), seed_instructions + machine_instructions)
                rouge_scores = [score["rougeL"].fmeasure for score in rouge_scores]
                # rouge_scores = [scorer.score(inst, e_inst)["rougeL"].fmeasure for e_inst in human_instructions + machine_instructions]
                if max(rouge_scores) > 0.7:
                    continue
                all_instructions = seed_instructions + machine_instructions
                most_similar_instructions = {
                        all_instructions[i] : rouge_scores[i] for i in np.argsort(rouge_scores)[-10:][::-1]
                    }
                machine_instructions.append(inst)
                               

                prompt = 'Can you extract the cause and effect pairs from the given pre-defined graph and return the result in json format? Here is an example:\nGiven the causal graph: The level of education has a direct effect on the income level. Whether the person has a high income level or not affects the person\'s accessibility to healthcare.\nThe cause and effect pairs are:\n{"pairs":[{"cause": "level of education","effect": "income level"},{"cause": "income level","effect": "accessibility to healthcare"}]}\nNow, given the causal graph: ' + inst + '\nReturn the cause and effect pairs in json as the previous example.'
                expand_result = make_gpt3_requests_chat(
                        engine=args.engine_chat,
                        messages=[{'role':'user', 'content':prompt}],
                        max_tokens=1024,
                        temperature=0.7,
                        top_p=0.5,
                        frequency_penalty=0,
                        presence_penalty=2,
                        api_key=args.api_key,
                        organization=args.organization)
                
                loop = 0
                while loop < 20:
                    expand_result = make_gpt3_requests_chat(
                        engine=args.engine_chat,
                        messages=[{'role':'user', 'content':prompt}],
                        max_tokens=1024,
                        temperature=0.7,
                        top_p=0.5,
                        frequency_penalty=0,
                        presence_penalty=2,
                        api_key=args.api_key,
                        organization=args.organization,
                    )
                    loop += 1  # 2 more pairs
                    
                    graph = expand_result["response"]['choices'][0]['message']['content'] # json format response
                    prompt = 'Can you continue constructing the graph with two more cause and effect pairs that expand from current nodes in the pre-defined causal graph? Remember to add the pairs in the json object directly and return. Here is an example:\nGiven the causal graph in json format:\n{"pairs": [{"cause": "level of education", "effect": "income level"}, {"cause": "income level", "effect": "accessibility to healthcare"}]}\nAdding two more cause and effect pairs, the causal graph is:\n{"pairs": [{"cause": "level of education", "effect": "income level"}, {"cause": "income level", "effect": "accessibility to healthcare"}, {"cause": "level of education", "effect": "professional skills"}, {"cause": "professional skills", "effect": "income level"}]}\nNow, given the causal graph in json format:\n' + str(graph) + '\nReturn the expanded causal graph in json as the previous example.'

                print(expand_result['response'])
                fout.write(json.dumps({
                    "instruction": inst,
                    "causal_graph": expand_result['response']['choices'][0]['message']['content'],
                    "most_similar": most_similar_instructions,
                    "avg_similarity_score": float(np.mean(rouge_scores)),
                    "metadata": metadata,
                    "request_idx": request_idx
                }) + "\n")
                progress_bar.update(1)
            request_idx += 1
            
            '''
            for prompt in batch_inputs:
                prompt = 'Can you extract the cause and effect pairs from the given pre-defined graph and return the result in json format? Here is an example:\nGiven the causal graph: The level of education has a direct effect on the income level. Whether the person has a high income level or not affects the person\'s accessibility to healthcare.\nThe cause and effect pairs are:\n{"pairs":[{"cause": "level of education","effect": "income level"},{"cause": "income level","effect": "accessibility to healthcare"}]}\nNow, given the causal graph: ' + prompt + '\nReturn the cause and effect pairs in json as the previous example.'
                result = make_gpt3_requests_chat(
                        engine=args.engine,
                        messages=[{'role':'user', 'content':prompt}],
                        max_tokens=1024,
                        temperature=0.7,
                        top_p=0.5,
                        frequency_penalty=0,
                        presence_penalty=2,
                        api_key=args.api_key,
                        organization=args.organization)
                
                loop = 0
                while loop <= 3:
                    result = make_gpt3_requests_chat(
                        engine=args.engine,
                        messages=[{'role':'user', 'content':prompt}],
                        max_tokens=1024,
                        temperature=0.7,
                        top_p=0.5,
                        frequency_penalty=0,
                        presence_penalty=2,
                        api_key=args.api_key,
                        organization=args.organization,
                    )
                    loop += 1
                    
                    graph = result["response"]['choices'][0]['message']['content'] # json format response
                    prompt = 'Can you continue constructing the graph with two more cause and effect pairs that expand from current nodes in the pre-defined causal graph? Remember to add the pairs in the json object directly and return. Here is an example:\nGiven the causal graph in json format:\n{"pairs": [{"cause": "level of education", "effect": "income level"}, {"cause": "income level", "effect": "accessibility to healthcare"}]}\nAdding two more cause and effect pairs, the causal graph is:\n{"pairs": [{"cause": "level of education", "effect": "income level"}, {"cause": "income level", "effect": "accessibility to healthcare"}, {"cause": "level of education", "effect": "professional skills"}, {"cause": "professional skills", "effect": "income level"}]}\nNow, given the causal graph in json format:\n' + str(graph) + '\nReturn the expanded causal graph in json as the previous example.'

                
                expanded_prompts.write(prompt + '\n')
                print(result) 
                # 替换成文字
                machine_instructions.append(result['response'])
                fout.write(json.dumps({
                    "gpt_chat": result['response'],
                    "request_idx": request_idx
                }) + "\n")
                request_idx += 1
                print(len(machine_instructions))
                

                
                new_instructions = result["response"]
                instructions += new_instructions
                all_metadata += [result] * len(new_instructions)
            
            for inst, metadata in zip(instructions, all_metadata):
                machine_instructions.append(inst)
                fout.write(json.dumps({
                    "gpt_chat": metadata,
                    "request_idx": request_idx
                }) + "\n")
                progress_bar.update(1)
            request_idx += 1
                '''
