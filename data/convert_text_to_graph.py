import json
import sys
sys.path.append('..')
from self_instruct.gpt3_api import make_requests as make_gpt3_requests

with open('causal_pairs.json', 'w') as fout:
    seed_tasks = [task for task in json.loads(open('gpt3_seeds.json', 'r').read())]
    seed_backgrounds = [t['background'] for t in seed_tasks]
    
    for seed in seed_backgrounds:
        prompt = 'Can you extract the cause and effect pairs from the given pre-defined graph and return the result in json format? Here is an example:\nGiven the causal graph: The level of education has a direct effect on the income level. Whether the person has a high income level or not affects the person\'s accessibility to healthcare.\nThe cause and effect pairs are:\n{"pairs":[{"cause": "level of education","effect": "income level"},{"cause": "income level","effect": "accessibility to healthcare"}]}\nNow, given the causal graph: ' + seed + '\nReturn the cause and effect pairs in json as the previous example.'
        result = make_gpt3_requests(
                        engine='gpt-3.5-turbo',
                        messages=[{'role':'user', 'content':prompt}],
                        max_tokens=1024,
                        temperature=0.7,
                        top_p=0.5,
                        frequency_penalty=0,
                        presence_penalty=2,
                        api_key='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'
                        )
        pairs = result['response']['choices'][0]['message']['content']
        
        fout.write(json.dumps({
            "background": str(pairs),
            "is_classification": False} + '\n'))

fout.close()
