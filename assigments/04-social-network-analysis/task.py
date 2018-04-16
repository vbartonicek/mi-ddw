# import
import csv
import pprint
import nltk
import networkx as netx
from networkx.drawing.nx_agraph import graphviz_layout
import matplotlib.pyplot as plt


# Object representing one input line
class Record:
    def __init__(self, record):
        self.code = self.parse(record, 0)
        self.movie = self.parse(record, 1)
        self.actor = self.parse(record, 2)
        self.genre = self.parse(record, 3)
        self.role = self.parse(record, 4)

    @staticmethod
    def parse(property, index):
        try:
            record = property[index].strip('"')
            if (record == ''):
                return "Unknown"
            else:
                return record
        except IndexError:
            return 'Unknown'


# Load and parse text from csv file
def get_data(file_name):
    data = []
    records = []

    # parse input file
    with open(file_name, 'r') as file:
        csv_reader = csv.reader(file, delimiter=',')
        for row in csv_reader:
            data.append(row)

    # create array of objects
    for row in data:
        row_split = row[0].split(';')
        records.append(Record(row_split))

    return records


# Create graph and count statistics
def create_graph(graph, records, actor_name):
    movies = {}

    for record in records:
        # Create node for each actor
        graph.add_node(record.actor)

        # Get actor list for each movie
        if (record.movie) not in movies:
            movies[record.movie] = []
        movies[record.movie].append(record.actor)

    # Add edges between actors
    for movie, actors in movies.items():
        for actor in actors:
            for next_actor in actors:
                if (actor != next_actor):
                    if (actor_name == '' or actor_name == actor or actor_name == next_actor):
                        graph.add_edge(actor, next_actor)


def printStatistics(graph):
    nodes_count = graph.number_of_nodes()
    edges_count = graph.number_of_edges()
    density = edges_count / (nodes_count * (nodes_count - 1) / 2)
    components_count = netx.number_connected_components(graph)

    print('=' * 10)
    print('Nodes = ', nodes_count)
    print('Edges = ', edges_count)
    print('Density = ', density)
    print('Components = ', components_count)
    print('=' * 10)


# Draw communities
def draw_communities(graph):
    communities = {node: cid + 1 for cid, community in
                   enumerate(netx.algorithms.community.k_clique_communities(graph, 3)) for node in
                   community}

    pos = graphviz_layout(graph)
    plt.figure(figsize=(10, 10))
    netx.draw(graph, pos, font_size=8,
              labels={v: str(v) for v in graph},
              cmap=plt.get_cmap("rainbow"),
              node_color=[communities[v] if v in communities else 0 for v in graph])
    plt.savefig("output/communities_short.png")
    # plt.show()


def draw_centralities(graph):
    centralities = [netx.degree_centrality, netx.closeness_centrality,
                    netx.betweenness_centrality, netx.eigenvector_centrality]
    region = 220
    plt.figure(figsize=(18, 18))
    for centrality in centralities:
        region += 1
        plt.subplot(region)
        plt.title(centrality.__name__)
        pos = netx.random_layout(graph)
        netx.draw(graph, pos, font_size=8, labels={v: str(v) for v in graph},
                  cmap=plt.get_cmap("bwr"), node_color=[centrality(graph)[k] for k in centrality(graph)])
    plt.savefig("output/entralities.png")
    # plt.show()


def analyse_data(records, actor):
    graph = netx.Graph()
    create_graph(graph, records, actor)

    # draw_communities(graph)
    # draw_centralities(graph)

    printStatistics(graph)

    # write to GEXF
    netx.write_gexf(graph, "output/export.gexf")


text_file = 'data/casts_complete.csv'
records = get_data(text_file)

analyse_data(records, '')
# analyse_data(records, 'Kevin Bacon')
