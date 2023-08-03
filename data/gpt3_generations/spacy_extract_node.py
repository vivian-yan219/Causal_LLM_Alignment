import spacy
import textacy

# load a spacy engine thru: python -m spacy download en_core_web_sm
nlp = spacy.load('en_core_web_sm')

# prepare a list of sentences that we will be processing
prompt = ['Whether the patient eats citrus has a direct effect on whether the patient has sufficient vitamin C .', 'Whether the patient has sufficient vitamin C has a direct effect on whether the patient recovers from scurvy.']

#for word in sentence:
#    print(word.text, word.pos_, word.dep_)

# find verb phrases
  # compile regex-like patterns for the part of speech combinations of words that make up the verb phrase
verb_patterns = [[{'POS':'VERB'}, {'POS':'DET'}, 
                {'POS':'ADJ'}, {'POS':'NOUN'}, {'POS':'ADP'}], # has a direct effect on
                [{'POS':'ADV'}, {'POS':'VERB'}]] # directly causes

# whether a verb phrase contains the root of the sentence
  # root: main verb of the sentence
def contains_root(verb_phrase, root):
    vp_beg = verb_phrase.start
    vp_end = verb_phrase.end

    if (root.i >= vp_beg and root.i <= vp_end):
        return True
    else:
        return False

# find the root of the sentence
def find_root(sentence):
    root_token = None
    for token in sentence:
        if (token.dep_ == 'ROOT'):
            root_token = token
    return root_token

# get verb phrases from a spacy object
def get_verb_phrases(sentence, verb_patterns):
    root = find_root(sentence)
    verb_phrases = textacy.extract.matches.token_matches(sentence, verb_patterns)

    new_vps = []
    for verb_phrase in verb_phrases:
        if contains_root(verb_phrase, root):
            new_vps.append(verb_phrase)
    return new_vps

# look for noun phrases on left- or right-side of the root verb phrase
def find_noun_phrase(verb_phrase, noun_phrases, side):
    for noun_phrase in noun_phrases:
        if side == 'left' and noun_phrase.end < verb_phrase.start:
            for word in noun_phrase:
                if word.dep_ != 'nsubj':
                    print(word, noun_phrase)
                    continue
            return noun_phrase
        elif side == 'right' and noun_phrase.start > verb_phrase.end:
            for word in noun_phrase:
                if word.dep_ != 'nsubj':
                    print(word, noun_phrase)
                    continue
            return noun_phrase
    

# find triplets of subject-relation-object in the sentence
def find_triplets(prompt):
    nodes = []
    edges = []
    for p in prompt:
        sentence = nlp(p)
        for word in sentence:
            print(word.text, word.pos_, word.dep_)
        verb_phrases = get_verb_phrases(sentence, verb_patterns)
        noun_phrases = sentence.noun_chunks
        
        verb_phrase = None
        for vp in verb_phrases:
            verb_phrase = vp

        cause = find_noun_phrase(verb_phrase, noun_phrases, 'left')
        effect = find_noun_phrase(verb_phrase, noun_phrases, 'right')
        nodes.append(cause)
        nodes.append(effect)
        edges.append((cause, effect))

    print(edges)

find_triplets(prompt)
