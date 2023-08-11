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
'''
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

vertices = ['police officer wears a bulletproof vest', 'police officer is shot', 'person dies', 'safety of police officer', "police officer's survival", 'person survives', 'gunshot wound severity', "police officer's recovery", 'injury prevention', "person's safety", 'bulletproof vest effectiveness', 'professional skills', 'accessibility to healthcare', "person's health"]
edges = [("police officer wears a bulletproof vest", "police officer is shot"),("police officer is shot", "person dies"), ( "police officer wears a bulletproof vest", "safety of police officer"), ( "safety of police officer", "police officer's survival"), ( "police officer is shot", "safety of police officer"), ( "safety of police officer", "person survives"), ( "police officer wears a bulletproof vest", "person survives"), ( "person survives", "police officer's survival"), ( "police officer wears a bulletproof vest", "person dies"), ( "person dies", "police officer's survival"), ( "police officer wears a bulletproof vest", "police officer's survival"), ( "police officer's survival", "person survives"), ( "police officer wears a bulletproof vest", "gunshot wound severity"), ( "gunshot wound severity", "police officer's recovery"), ( "police officer is shot", "gunshot wound severity"), ( "gunshot wound severity", "person dies"), ( "police officer wears a bulletproof vest", "injury prevention"), ( "injury prevention", "police officer's safety"), ( "police officer is shot", "injury prevention"), ( "injury prevention", "person's safety"), ( "police officer wears a bulletproof vest", "gunshot wound severity"), ( "gunshot wound severity", "person's safety"), ( "police officer wears a bulletproof vest", "bulletproof vest effectiveness"), ( "bulletproof vest effectiveness", "police officer's survival"), ( "police officer is shot", "bulletproof vest effectiveness"), ( "bulletproof vest effectiveness", "person survives"), ( "police officer wears a bulletproof vest", "professional skills"), ( "professional skills", "police officer's performance"), ( "police officer is shot", "professional skills"), ( "professional skills", "person's safety"), ( "police officer wears a bulletproof vest", "police officer's recovery"), ( "police officer's recovery", "person survives"), ( "police officer wears a bulletproof vest", "person dies"), ( "person dies", "police officer's recovery"), ( "police officer wears a bulletproof vest", "police officer's survival"), ( "police officer's survival", "safety of police officer"), ( "police officer's survival", "person survives"), ( "police officer's survival", "gunshot wound severity"), ( "police officer's survival", "injury prevention"), ( "police officer's survival", "bulletproof vest effectiveness"), ( "police officer's survival", "professional skills"), ( "police officer is shot", "person's safety"), ( "person's safety", "police officer's survival"), ( "person's safety", "gunshot wound severity"), ( "person's safety", "injury prevention"), ( "person's safety", "bulletproof vest effectiveness"), ( "person's safety", "professional skills"), ( "police officer wears a bulletproof vest", "safety of police officer"), ( "safety of police officer", "person dies"), ( "police officer is shot", "professional skills"), ( "professional skills", "person dies"), ( "police officer wears a bulletproof vest", "accessibility to healthcare"), ( "accessibility to healthcare", "police officer's health"), ( "police officer is shot", "accessibility to healthcare"), ( "accessibility to healthcare", "person's health"), ( "police officer wears a bulletproof vest", "resistance to bullets"), ( "resistance to bullets", "bullet penetration"), ( "police officer is shot", "resistance to bullets")]
dag = graphs.DAG(vertices, edges)
dag.draw().view()
'''
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
