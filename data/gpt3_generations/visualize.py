'''
from ananke.graphs import ADMG
from ananke.identification import OneLineID
from ananke.estimation import CausalEffect
from ananke.datasets import load_afixable_data
from ananke.estimation import AutomatedIF
'''
import json
import numpy as np
from ananke import graphs
from ananke import identification

with open('machine_generated_instructions.json') as fin:
    data = fin.readlines()
    vs = []
    es = []
    for case in data:
        expanded_graph = json.loads(json.loads(case)['causal_graph'])['pairs']
        v = set()
        e = set()
        p = 0
        for pair in expanded_graph:
            cause = pair['cause']
            effect = pair['effect']
            v.add(cause)
            v.add(effect)
            e.add((cause, effect))
            dag = graphs.DAG(v, e)
            dag.draw().view()
            p += 1
        print(p)
        break
        vs.append(v)
        es.append(e)

'''
vertices = ['patient eat citrus', 
            'patient has sufficient vitamin C',
            'patient recovers from scurvy', 
            'patient\'s immune system strengthens', 
            'patient fights off infections',
            'patient\'s overall health improves',
            'patient has more energy']
edges = [('patient eat citrus', 'patient has sufficient vitamin C'), 
        ('patient has sufficient vitamin C', 'patient recovers from scurvy'),
        ('patient eat citrus', 'patient\'s immune system strengthens'),
        ('patient\'s immune system strengthens', 'patient fights off infections'),
        ('patient has sufficient vitamin C', 'patient\'s overall health improves'),
        ('patient\'s overall health improves', 'patient has more energy')]
dag = graphs.DAG(vertices, edges)
dag.draw().view()

v2 = ['gender', 'smoking or not',
      'high tar deposit in lungs',
      'lung cancer',
      'heart disease',
      'shortness of breath',
      ]
e2 = [('gender', 'smoking or not'),
        ('smoking or not', 'high tar deposit in lungs'),
        ('high tar deposit in lungs', 'lung cancer'),
        ('gender', 'lung cancer'),
        ('gender', 'heart disease'),
        ('heart disease','shortness of breath'),
        ('smoking or not', 'heart disease'),
        ('heart disease','shortness of breath')]
dag2 = graphs.DAG(v2, e2)
dag2.draw().view()
'''
