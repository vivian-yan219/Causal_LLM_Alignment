import json
import sys

fout_gen = open('compile_machine_generated_instructions.json', 'w')
fout_qa = open('compile_machine_generated_qas.json', 'w')

with open('machine_generated_instructions.json', 'r') as fin_gen:
    lines = fin_gen.readlines()
    for line in lines:
        fout_gen.write(json.dumps(json.loads(line), indent = 2))

with open('machine_generated_instances.json', 'r') as fin_qa:
    lines = fin_qa.readlines()
    for line in lines:
        fout_qa.write(json.dumps(json.loads(line), indent = 2))

fin_gen.close()
fout_gen.close()
fin_qa.close()
fout_qa.close()
