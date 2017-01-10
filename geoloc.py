from __future__ import print_function
from flask import Flask, render_template, request, flash, redirect
import os
import re

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_STATIC = os.path.join(APP_ROOT, 'static')


app = Flask(__name__)
app.secret_key = 'f65gh099x'


def create_data_dict(file, ref_header, delimiter=','):

    import csv
    reader = csv.DictReader(open(os.path.join(APP_STATIC, file)), delimiter=delimiter)
    result = {}
    for row in reader:
        key = row.pop(ref_header)
        result[key] = row
    return result

# Create a dict containing the CSV data using OBJECTID as the key
townlands_dict = create_data_dict('townlands.csv', 'OBJECTID')

# Create a second dict with the English Name as the key and the OBJECTIDs as a list of values (deals with duplicate townland names)
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

# Search the id_dictionary for the user inputted search term(s), stop at first match, output a list of matching OBJECTIDs
def search_id_dict(dict, searchTermList):
    for term in searchTermList:
        try:
            if dict[term]:
                return dict[term]
        except KeyError, error:
            continue
    return []

# Fetch the coordinates from the data_dictionary that match the OBJECTIDs from the previous search
def retrieve_from_data_dict(list, data_dict):
    coord_list = []
    for i in list:
        try:
            X = data_dict[i]['X']
            Y = data_dict[i]['Y']
            name = data_dict[i]['English_Name']
            coords = X, Y, name
            coord_list.append(coords)
        except KeyError, error:
            continue
    return coord_list

# Prepare the search terms from the form as a list, call the required function, render the html
@app.route('/', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = str(request.form.get('search'))
        query = query.upper()
        query = filter(None, re.split("[, \-!?:]+", query))
        returned_id_list = search_id_dict(id_dict, query)
        if returned_id_list == []:
            flash("No match for those search terms!")
            return redirect('/')
        else:
            results = retrieve_from_data_dict(returned_id_list, townlands_dict)
    else:
        results = ''
    return render_template("index.html", results=results)


if __name__ == '__main__':
    app.run()

