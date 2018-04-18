# import
import csv
import networkx as netx


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

    print("\nSTATISTICS:\n")
    print('Nodes = ', nodes_count)
    print('Edges = ', edges_count)
    print('Density = ', density)
    print('Components = ', components_count)
    print('=' * 10)


# Get communities
def get_communities(graph):
    communities = {node: cid + 1 for cid, community in
                   enumerate(netx.algorithms.community.k_clique_communities(graph, 3)) for node in
                   community}

    community_to_actors = {}
    for key, val in communities.items():
        if val not in community_to_actors:
            community_to_actors[val] = []
        community_to_actors[val].append(key)

    for actor, community_id in communities.items():
        graph.node[actor]['community_id'] = community_id

    communities_sorted = sorted(community_to_actors.items(), key=lambda element: len(element[1]),
                                            reverse=True)

    print("\nTOP COMMUNITIES:\n")
    for community in communities_sorted[:3]:
        print("Community ID = {}".format(community[0]))
        print('Actors count= {}'.format(len(community[1])))
        print('Actors = {}'.format(community[1]))
        print('=' * 10)


# Get centralities
def get_centralities(graph):
    centralities = [netx.degree_centrality, netx.closeness_centrality,
                    netx.betweenness_centrality, netx.eigenvector_centrality]
    index = 0

    for centrality in centralities:
        index += 1
        title = "centrality_{}".format(index)
        results = centrality(graph)

        for actor, value in results.items():
            graph.node[actor][title] = value

        centralities_sorted = sorted(results.items(), key=lambda element: element[1], reverse=True)

        print("\nTOP CENTRALITY_{}:\n".format(index))
        for centrality in centralities_sorted[:3]:
            print("Actor = {}".format(centrality[0]))
            print('Centrality = {}'.format(centrality[1]))
            print('=' * 10)


def analyse_data(records, actor):
    graph = netx.Graph()
    create_graph(graph, records, actor)

    printStatistics(graph)

    get_communities(graph)
    get_centralities(graph)

    # write to GEXF
    netx.write_gexf(graph, "output/export.gexf")


text_file = 'data/casts_complete.csv'
records = get_data(text_file)

analyse_data(records, '')
# analyse_data(records, 'Kevin Bacon')
