# import
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
import numpy as np
import csv

d_files_count = 1400
q_files_count = 225


# Represent each document and query using the Vector Space Model with all following weightings:
# Use Binary representation
def get_binary(data):
    vectorizer = CountVectorizer(binary=True)
    matrix = vectorizer.fit_transform(data)
    return matrix


# Use pure Term Frequency
def get_term(data):
    vectorizer = CountVectorizer(binary=False)
    matrix = vectorizer.fit_transform(data)
    return matrix


# Use TF-IDF
def get_td_idf(data):
    # init vectorizer
    vectorizer = TfidfVectorizer()

    # prepare matrix
    matrix = vectorizer.fit_transform(data)

    # compute similarity between query and all docs
    # sim = np.array(cosine_similarity(matrix[len(data) - 1], matrix[0:(len(data) - 1)])[0])
    return matrix


# Compute relevance scores for each combination of query, document
# Use Euclidean distance
def euclidean(matrix):
    sim = np.array(euclidean_distances(matrix[d_files_count], matrix[0:(d_files_count)])[0])
    sorted = sim.argsort() + 1
    return sorted[:20]


# Use Cosine similarity measure
def cosine(matrix):
    sim = np.array(cosine_similarity(matrix[d_files_count], matrix[0:(d_files_count)])[0])
    sorted = sim.argsort()[::-1] + 1
    return sorted[:20]


def get_relevant(query_id):
    relevant = []
    with open("./cranfield/r/" + str(query_id + 1) + ".txt") as file:
        for line in file.readlines():
            relevant.append(int(line))
    return relevant


# Evaluate quality and difference of both scores and different weighting schemas
# Compute Precision, Recall, F-measure (you can limit to top N relevant documents for each query)

def get_precision(retrieved, relevant):
    relevant_count = 0
    for doc in retrieved:
        if doc in relevant:
            relevant_count += 1

    return relevant_count / len(retrieved)


def get_recall(retrieved, relevant):
    relevant_count = 0
    for doc in retrieved:
        if doc in relevant:
            relevant_count += 1

    return relevant_count / len(relevant)


def get_f_measure(precision, recall):
    if precision == 0 and recall == 0:
        return 0

    return 2 * (precision * recall) / (precision + recall)


# Process data for specific method - Binary, Term or TD-IDF
def process_method(data, rel, method):
    if method == 'binary':
        binary = get_binary(data)
        cos = cosine(binary)
        euclid = euclidean(binary)
    elif method == 'term':
        term = get_term(data)
        cos = cosine(term)
        euclid = euclidean(term)
    elif method == 'td_idf':
        td_idf = get_td_idf(data)
        cos = cosine(td_idf)
        euclid = euclidean(td_idf)

    # Cosine similarity measure
    cos_precision = get_precision(cos, rel)
    cos_recall = get_recall(cos, rel)
    cos_f_measure = get_f_measure(cos_precision, cos_recall)

    # Euclidean distance
    euclid_precision = get_precision(euclid, rel)
    euclid_recall = get_recall(euclid, rel)
    euclid_f_measure = get_f_measure(euclid_precision, euclid_recall)

    return [cos_precision, cos_recall, cos_f_measure, euclid_precision, euclid_recall, euclid_f_measure]


# Process input files and create output file
def process_data():
    with open("output.csv", 'w') as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow(["query",
                         "Binary cos precision", "Binary cos recall", "Binary Cosine f_measure",
                         "Binary euclid precision", "Binary euclid recall", "Binary euclid f_measure",
                         "Term cos precision", "Term cos recall", "Term cos f_measure",
                         "Term euclid precision", "Term euclid recall", "Term cos f_measure",
                         "Tf_idf cos precision", "Tf_idf cos recall", "Tf_idf cos f_measure",
                         "Tf_idf euclid precision", "Tf_idf euclid recall", "Tf_idf euclid f_measure",
                         ])

        # prepare corpus
        corpus = []
        for d in range(d_files_count):
            f = open("./cranfield/d/" + str(d + 1) + ".txt")
            corpus.append(f.read())
        # add query to corpus
        for q in range(q_files_count):
            f = open("./cranfield/q/" + str(q + 1) + ".txt")
            # corpus.append(f.read())
            data = list(corpus)
            data.append(f.read())

            row_builder = [q + 1]

            rel = get_relevant(q)
            row_builder += process_method(data, rel, 'binary')
            row_builder += process_method(data, rel, 'term')
            row_builder += process_method(data, rel, 'td_idf')

            writer.writerow(row_builder)


process_data()
