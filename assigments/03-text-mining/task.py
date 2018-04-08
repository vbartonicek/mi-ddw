# import
import nltk
import wikipedia
import csv

text_file = 'harry-potter-short.txt'


# Load text from input file
def get_data(file_name):
    with open(file_name, 'r') as f:
        input_text = f.read()
    return input_text


# Get POS Tags
def get_pos_tags(text):
    sentences = nltk.sent_tokenize(text)
    tokens = [nltk.word_tokenize(sent) for sent in sentences]
    tagged = [nltk.pos_tag(sent) for sent in tokens]
    return tagged


# Get named entities - Lecture 4 - slide 37
def get_named_entities(text):
    tokens = nltk.word_tokenize(text)
    tagged = nltk.pos_tag(tokens)
    ne_chunked = nltk.ne_chunk(tagged, binary=True)

    data = {}
    for entity in ne_chunked:
        if isinstance(entity, nltk.tree.Tree):
            text = " ".join([word for word, tag in entity.leaves()])
            ent = entity.label()

            if text not in data:
                data[text] = [ent, 0]
            data[text][1] += 1
        else:
            continue

    return data


# Process single entity
def add_entity(entity, tagged_entities):
    entity_str = " ".join([word[0] for word in entity])
    if entity_str not in tagged_entities:
        tagged_entities[entity_str] = [entity, 0]
    tagged_entities[entity_str][1] += 1

    return tagged_entities


# Get custom parsed entities
def get_custom_entities(tagged_list):
    tagged_entities = {}
    entity = []

    adjectives = ['JJ']
    determiners = ['DT']
    nouns = ['NNP', 'NNPS']

    for tagged_sentence in tagged_list:
        for tagged_word in tagged_sentence:
            word_tag = tagged_word[1]
            if not entity:
                if word_tag in determiners + adjectives:
                    entity.append(tagged_word)
                    continue

                elif word_tag in nouns:
                    entity.append(tagged_word)
                    tagged_entities = add_entity(entity, tagged_entities)

            else:
                if entity[-1][1] in determiners + adjectives:
                    if word_tag in adjectives:
                        entity.append(tagged_word)
                        continue

                    elif word_tag in nouns:
                        entity.append(tagged_word)
                        tagged_entities = add_entity(entity, tagged_entities)

            entity = []

    return tagged_entities


# Find entity on Wikipedia
def find_on_wiki(entity: str):
    page = wikipedia.page(entity)
    wiki_tagged_tokens = nltk.pos_tag(nltk.word_tokenize(page.summary))
    grammar = "NP: {<DT>?<JJ>*<NN>}"
    cp = nltk.RegexpParser(grammar)
    chunked = cp.parse(wiki_tagged_tokens)

    for entity in chunked:
        if isinstance(entity, nltk.tree.Tree):
            wiki_text = " ".join([word for word, tag in entity.leaves()])
            return wiki_text
        else:
            continue


# POS tagging
def process_pos_tagging(tokens):
    with open("pos_tagging.csv", 'w') as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow([tokens])
    file.close()


# NER with entity classification
def process_ner_entity(entities):
    sorted_entities = sorted(entities.items(), key=lambda entity: entity[1][1], reverse=True)

    with open("ner_entity_classification.csv", 'w') as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow([sorted_entities])
    file.close()


# NER with custom patterns
def process_ner_custom(entities):
    sorted_entities = sorted(entities.items(), key=lambda entity: entity[1][1], reverse=True)

    with open("ner_custom_patterns.csv", 'w') as file:
        writer = csv.writer(file, delimiter=";")
        for custom_entity in sorted_entities:
            writer.writerow(["{}x - {} - {}".format(custom_entity[1][1], custom_entity[0], custom_entity[1][0])])
    file.close()


# Tagged NLTK entities/custom entities through Wikipedia
def process_wikipedia(entities, filename):
    with open(filename + ".csv", 'w') as file:
        writer = csv.writer(file, delimiter=";")
        count = 0

        writer.writerow(["ENTITY -> WIKIPEDIA"])
        writer.writerow(["-------------------"])

        for entity in entities:
            try:
                category = find_on_wiki(entity)
                writer.writerow(["{} -> {}".format(entity, category)])
                count += 1
            except:
                pass
    file.close()


text = get_data(text_file)
tagged_tokens = get_pos_tags(text)
named_entities = get_named_entities(text)
custom_parsed_entities = get_custom_entities(tagged_tokens)

# POS tagging
process_pos_tagging(tagged_tokens)

# NER with entity classification
process_ner_entity(named_entities)

# NER with custom patterns
process_ner_custom(custom_parsed_entities)

# Tagged NLTK entities through Wikipedia
process_wikipedia(named_entities, "entities_wikipedia")

# Tagged custom entities through Wikipedia
process_wikipedia(custom_parsed_entities, "custom_entities_wikipedia")
