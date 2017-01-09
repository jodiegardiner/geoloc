from __future__ import print_function
from flask import Flask, render_template, request
import os

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_STATIC = os.path.join(APP_ROOT, 'static')


app = Flask(__name__)


def create_data_dict(file, ref_header, delimiter=','):

    import csv
    reader = csv.DictReader(open(os.path.join(APP_STATIC, file)), delimiter=delimiter)
    result = {}
    for row in reader:
        key = row.pop(ref_header)
        result[key] = row
    return result

townlands_dict = create_data_dict('townlands.csv', 'OBJECTID')


def create_id_dict(data_dict):
    result = {}
    for key, value in data_dict.iteritems():
        if value['English_Name'] not in result:
            id_list = []
            id_list.append(key)
            result[value['English_Name']] = id_list
        else:
            result[value['English_Name']].append(key)
    return result

id_dict = create_id_dict(townlands_dict)


def search_id_dict(dict, searchTermList):
    for term in searchTermList:
        try:
            if dict[term]:
                return dict[term]
        except KeyError, error:
            continue
    return []


def retrieve_from_data_dict(list, data_dict):
    coord_list = []
    for i in list:
        try:
            X = data_dict[i]['X']
            Y = data_dict[i]['Y']
            coords = X, Y
            coord_list.append(coords)
        except KeyError, error:
            continue
    return coord_list


@app.route('/', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = str(request.form.get('search'))
        query = query.upper()
        query = query.split(',')
        returned_id_list = search_id_dict(id_dict, query)
        results = retrieve_from_data_dict(returned_id_list, townlands_dict)
    else:
        results = ''
    print(results)
    return render_template("index.html", results=results)


if __name__ == '__main__':
    app.run()

