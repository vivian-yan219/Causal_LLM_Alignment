import yaml
from yaml.loader import SafeLoader
from graph import Graph
import template
import json

def get_background(graph, story):
    background = 'Provide more possible cause and effect pairs based on the following causal relations: '
    for node in graph.graph:
        if graph.graph[node]['parent']:
            for parent in graph.graph[node]['parent']:
                bg = "{} has a direct effect on {}.".format(
                        story['semantic'][parent] or 'unobserved confounders',
                        story['semantic'][node] or 'unobserved confounders'
                        )
                bg = bg[0].upper() + bg[1:]
                background += bg
    return background


config = open('config.yaml', 'r')
data = yaml.safe_load(config)
fout = open('seeds.json', 'w')

seeds = []
for name in data['story_list']:
    story = data['story_list'][name]
    graph = Graph(story['node'], story['edge'])
    generate_function = getattr(template, story['type'])
    instances = generate_function(graph, story, filter_invalid=True)
    
    if story.get('background', None):
        background = 'Given the following casual relations: '
        background += story['background'].split(':')[1].strip()
    else:
        background = get_background(graph, story)
    seeds.append({'name': name, 
                'type': story['type'], 
                'background': background, 
                'instances': instances})

fout.write(json.dumps(seeds, indent=2))
fout.close()
