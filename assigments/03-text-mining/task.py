# import
import nltk
from pprint import pprint

file = 'harry-potter-short.txt';

# Load text from input file
def get_data(file_name):
    with open(file_name, 'r') as f:
        text = f.read()
    return text[:500]

def get_pos_tags(text):
    sentences = nltk.sent_tokenize(text)
    tokens = [nltk.word_tokenize(sent) for sent in sentences]
    tagged = [nltk.pos_tag(sent) for sent in tokens]
    return tagged



# Lecture 4 - slide 37
def get_named_entities(text):
    tokens = nltk.word_tokenize(text)
    tagged = nltk.pos_tag(tokens)
    ne_chunked = nltk.ne_chunk(tagged, binary=True)

    data = {}
    for entity in ne_chunked:
        if isinstance(entity, nltk.tree.Tree):
            text = " ".join([word for word, tag in entity.leaves()])
            ent = entity.label()
            # data[text] = ent
            if text not in data:
                data[text] = [ent, 0]
            data[text][1] += 1
        else:
            continue

    return data


text = get_data(file)

tagged_tokens = get_pos_tags(text)
print("Tokens:")
pprint(tagged_tokens[:1])

print('--------')

named_entities = get_named_entities(text)
print("Top recognized entities:")
sorted_entities = sorted(named_entities.items(), key=lambda entity: entity[1][1], reverse=True)
pprint(sorted_entities[:10])