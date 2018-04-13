# import
import csv
import pprint


# Load text from csv file
def get_data(file_name):
    data = []

    with open(file_name, 'r') as file:
        csv_reader = csv.reader(file, delimiter=';')
        for row in csv_reader:
            data.append(row)

    return data


text_file = 'casts.csv'

text = get_data(text_file)
pprint.pprint(text)
