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
    data = list(reader)

    # render the results page
    labels_and_values = get_chart_labels(topic_num)
    print(labels_and_values)
    topics = labels_and_values[0]
    labels = labels_and_values[1]
    values = labels_and_values[2]
    return render_template('faq.html',
        curr_topic = topics[topic_num],
        questions_list=data,
        num_clusters=len(data),
        topics=topics,
        labels=labels,
        values=values)

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
        print(line_count)
        # add to list of topics
        print(row)
        if row != []:
            topics.append(row[0])
            if line_count == topic_number:
                print("hitting line count == topic number")
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
@app.route("/graph", methods=['GET'])
def show_graph():
    references_reader = csv.reader(references_file)
    nodes = []
    edges = []

    for row in references_reader:
        original_string = row[0]
        original_string = original_string[1: len(original_string) - 1]
        original_string = original_string.replace("[", "")
        original_string = original_string.replace("]", "")

        ids = original_string.split(',')
        source = ids[0]
        soure = source.replace(" ", "")
        ids.pop(0)

        if source not in nodes:
            if source != '-1':
                nodes.append(source)

        if source != '-1':
            for id in ids:
                id = id.replace(" ", "")
                if id != '-1':
                    if id not in nodes:
                        nodes.append(id)
                    edges.append([source, id])

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

# def get_question():
#     myDB.execute("SELECT question FROM CIS120")
#     question = myDB.fetchall()
#     return question
#
# def get_num_questions():
#     myDB.execute("SELECT COUNT(DISTINCT question_number) FROM CIS120")
#     num = myDB.fetchone()
#     return num[0]
#
# def get_num_contributions():
#     myDB.execute("SELECT COUNT(*) FROM CIS120")
#     num = myDB.fetchone()
#     return num[0]
#
# # Set up the database by parsing data and pushing it to aws
# def create_db():
#     print("IS THIS BEING CALLED")
#     # csv file name
#     filename = "contributions.csv"
#
#     myDB.execute("DROP TABLE CIS120")
#     myDB.execute("CREATE TABLE CIS120 (question_number INT, "+
#              "topic VARCHAR(500), subject VARCHAR(500), question VARCHAR(2000), answer VARCHAR(2000), num_times_referred_to INT, "+
#              "follow_up_number INT, endorsed INT, PRIMARY KEY(question_number, follow_up_number))")
#
#     fields = []
#     rows = []
#
#     # reading csv file
#     with open(filename, 'r', encoding="utf8") as csvfile:
#         # creating a csv reader object
#         csvreader = csv.reader(csvfile)
#
#         # extracting field names through first row
#         fields = next(csvreader)
#
#         # extracting each data row one by one
#         for row in csvreader:
#             rows.append(row)
#
#         curr_question = ""
#         curr_text = ""
#         curr_topic = ""
#         curr_folder = ""
#         curr_answer = ""
#         curr_number = 0
#         curr_follow_up = 0
#         endorsed = 0
#
#         # This will help us take the most recent version because it always comes first
#         already_filled = 0
#         for row in rows[:]:
#             # parsing each column of a row
#             for col,field in zip(row, fields):
#                 if(field == "Post Number" and curr_number != int(col)):
#                     if(curr_question != "" and curr_answer != ""):
#                         sql = "INSERT INTO CIS120 (question_number, subject, topic, question, answer, num_times_referred_to, "\
#                         "follow_up_number, endorsed) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
#                         val = (int(curr_number), curr_folder, curr_topic, curr_question, curr_answer, int(0), int(curr_follow_up), int(endorsed))
#                         myDB.execute(sql, val)
#                     curr_number = int(col)
#                     curr_follow_up = 0
#                     curr_question = ""
#                     curr_answer = ""
#                     curr_topic = ""
#                     endorsed = 0
#
#                 elif(field == "Submission HTML Removed"): #the question could also be in subject
#                     curr_text = col
#
#                 elif(field == "Subject"): #We want to check if this is actually the question eventaully
#                     curr_topic = col
#
#                 elif(field == "Folders"):
#                     curr_folder = col
#
#                 elif(field == "Endorsed by Instructor"):
#                     if(col == "TRUE"):
#                         endorsed = 1
#                     else:
#                         endorsed = 0
#
#                 elif(field == "Part of Post"):
#                     if(col == "started_off_question"):
#                         if(already_filled != 1):
#                             curr_question = curr_text
#                         alread_filled = 0
#                     elif(col == "updated_question"):
#                         # update question entry to post and follow up numbers
#                         if(already_filled != 1):
#                             curr_question = curr_text
#                             already_filled = 1
#
#                     elif(col == "updated_i_answer"):
#                         # update last entry to the post and follow up number
#                         # what if it was appended? how do we update just the end?
#                         if(already_filled != 1):
#                             curr_answer = curr_answer + "\n" + curr_text
#                             already_filled = 1
#                         endorsed = 1
#                     elif(col == "started_off_i_answer"):
#                         if(already_filled != 1):
#                             curr_answer = curr_answer + "\n" + curr_text
#                         alread_filled = 0
#                         endorsed = 1
#
#                     elif(col == "updated_s_answer"):
#                         # update last entry to the post and follow up number
#                         # what if it was appended? how do we update just the end?
#                         if(already_filled != 1):
#                             curr_answer = curr_answer + "\n" + curr_text
#                             already_filled = 1
#                     elif(col == "started_off_s_answer"):
#                         # append to answer - if it was previously endorsed and were appending should we keep it endorsed?
#                         if(already_filled != 1):
#                             curr_answer = curr_answer + "\n" + curr_text
#                         alread_filled = 0
#
#                     elif(col == "followup"):
#                         # new entry for the new followup question
#                         if(curr_question != ""):
#                             sql = "INSERT INTO CIS120 (question_number, subject, topic, question, answer, num_times_referred_to, "\
#                             "follow_up_number, endorsed) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
#                             val = (int(curr_number), curr_folder, curr_topic, curr_question, curr_answer, int(0), int(curr_follow_up), int(endorsed))
#                             myDB.execute(sql, val)
#                             curr_question = ""
#                             curr_answer = ""
#                             endorsed = 0
#
#                         curr_follow_up = curr_follow_up + 1
#                         curr_question = curr_text
#                     elif(col == "reply_to_followup"):
#                         curr_answer = curr_answer + "\n" + curr_text

if __name__ == "__main__":
    #create_db()
    app.run()
