import yaml
from yaml.loader import SafeLoader
from graph import Graph
import template
import json

def get_background(graph, story):
    #background = 'Expand the causal graph by providing two more cause and effect pairs: '
    background = ''
    for node in graph.graph:
        if graph.graph[node]['parent']:
            for parent in graph.graph[node]['parent']:
                bg = "{} has a direct effect on {}.".format(
                        story['semantic'][parent] or 'unobserved confounders',
                        story['semantic'][node] or 'unobserved confounders'
                        )
                bg = bg[0].upper() + bg[1:]
                background = background + bg + ' '
    return background.strip()


config = open('config.yaml', 'r')
data = yaml.safe_load(config)
fout = open('gpt3_seeds.json', 'w')

seeds_lst = []
for name in data['story_list']:
    story = data['story_list'][name]
    graph = Graph(story['node'], story['edge'])
    generate_function = getattr(template, story['type'])
    instances = generate_function(graph, story, filter_invalid=True)
    
    if story.get('background', None):
        #background = 'Expand the causal graph by providing two more cause and effect pairs: '
        background = story['background']
    else:
        background = get_background(graph, story)
    seeds = {'name': name, 
             'type': story['type'], 
             'background': background, 
             'instances': instances,
             'is_classification': False}
    seeds_lst.append(seeds)
    
fout.write(json.dumps(seeds_lst, indent=2))
fout.close()
