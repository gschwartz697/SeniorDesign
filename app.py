#import pymysql
import json
import csv
import cgi
import os
import datetime

from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import timedelta, date, time

UPLOAD_FOLDER = 'PythonScripts'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#myDB = pymysql.connect(host="seniordesign.cbvhmgr3ve3r.us-east-2.rds.amazonaws.com",port=3306,user="grlpwr",passwd="ourseniordesignproject",db="seniordesign")
#myDB = myDB.cursor()


f = open('results.csv')
hw_timestamps_file = open('PythonScripts/hw_timestamps.csv')
references_file = open('PythonScripts/references.csv')
output_file = open('PythonScripts/output_120_all.csv')

@app.route("/", methods=['GET', 'POST'])
def main():
    if request.method == 'GET':
        return render_template('upload.html')
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # need to parse saved file here
            print("showing results")
            return show_results(0)

def show_results(topic_num):
    reader = csv.reader(f)
    data = ["Sample question 1", "Sample question 2", "Sample question 3"]

    questions_list = get_faq()

    # render the results page
    labels_and_values = get_chart_labels(topic_num)
    #print(labels_and_values)
    topics = labels_and_values[0]
    labels = labels_and_values[1]
    values = labels_and_values[2]
    return render_template('faq.html',
        curr_topic = topics[topic_num],
        questions_list=questions_list,
        num_clusters=len(data),
        topics=topics,
        labels=labels,
        values=values)

def get_faq():
    output_reader = csv.reader(output_file)
    topics_to_questions = []
    current_topic = []
    for row in output_reader:
        if not row[1]:
            # start of a new topic
            topics_to_questions.append(current_topic)
            current_topic = []
            current_topic.append(row[0])
        if row[1]:
            # add questions to the current cluster
            current_cluster = []
            for col in row:
                if col != '':
                    current_cluster.append(col)

            current_topic.append(current_cluster)
    topics_to_questions.pop(0)
    return topics_to_questions

# getting chart for specific topic
@app.route("/chart/<int:topic_num>", methods=['GET'])
def get_new_chart(topic_num):
    hw_timestamps_file.seek(0)
    return show_results(topic_num)

def get_chart_labels(topic_number):
    # read from generated file
    hw_timestamps_file.seek(0)
    hw_timestamps_reader = csv.reader(hw_timestamps_file)

    line_count = 0
    topics = []
    labels = []
    final_values = []
    print(topic_number)

    for row in hw_timestamps_reader:
        #print(line_count)
        # add to list of topics
        #print(row)
        if row != []:
            topics.append(row[0])
            if line_count == topic_number:
                #print("hitting line count == topic number")
                # get range of dates
                dates = row[1].split(',')
                dates.pop(len(dates) - 1)
                dates.sort()
                first = datetime.datetime.strptime(dates[0], "%m/%d/%Y")
                last = datetime.datetime.strptime(dates[len(dates) - 1], "%m/%d/%Y")

                # create labels (all dates in range)
                for dt in daterange(first, last):
                    labels.append(dt.strftime("%m/%d/%Y"))
                    #print(dt.strftime("%m/%d/%Y"))

                #print(labels)

                # assign values from given info
                values = [0] * len(labels)
                index = 0
                for post_date in dates:
                    if index < len(dates) - 1:
                        date_index = labels.index(post_date)
                        values[date_index] += 1
                        index += 1
                    else:
                        index += 1

                #print(labels)
                #print(values)
                final_values = values
            line_count += 1

    return [topics, labels, final_values]

# getting graph for referenced homeworks
@app.route("/graph/<curr_topic>", methods=['GET'])
def show_graph(curr_topic):
    references_file.seek(0)
    references_reader = csv.reader(references_file)
    nodes = []
    edges = []
    in_topic = False

    for row in references_reader:
        if row != []:
            if row[0] == curr_topic:
                in_topic = True
            elif in_topic:
                # check if line starts with a number
                str = row[0]
                if str[0].isdigit():
                    # add nodes and edges
                    source = str
                    ids = row[1]
                    ids = ids.replace("[", "")
                    ids = ids.replace("]", "")
                    dests = ids.split(',')

                    if source not in nodes:
                        if source != '-1':
                            nodes.append(source)

                    if source != '-1':
                        for id in dests:
                            id = id.replace(" ", "")
                            if id != '-1':
                                if id not in nodes:
                                    nodes.append(id)
                                edges.append([source, id])
                else:
                    # end of the current topic
                    in_topic = False
                    break
    print(nodes)
    print(edges)

    return render_template('graph.html',
        nodes = nodes,
        edges = edges)

def daterange(date1, date2):
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + timedelta(n)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file():
    print(request.files)
    form = cgi.FieldStorage()
    print(form)
    fileitem = request.files["fileUpload"]
    if fileitem.file:
        linecount = 0
        while 1:
            line = fileitem.file.readline()
            print(line)
            if not line: break
            linecount = linecount + 1

if __name__ == "__main__":
    #create_db()
    app.run()
