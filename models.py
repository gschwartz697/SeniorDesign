
import pymysql
import csv
  
# Set up the database by parsing data and pushing it to aws
def create_db():
    print("IS THIS BEING CALLED")
    # csv file name 
    filename = "contributions.csv"

    myDB = pymysql.connect(host="seniordesign.cbvhmgr3ve3r.us-east-2.rds.amazonaws.com",port=3306,user="grlpwr",passwd="ourseniordesignproject",db="seniordesign")
    myDB = myDB.cursor()

    myDB.execute("DROP TABLE CIS120")
    myDB.execute("CREATE TABLE CIS120 (question_number INT, "+
             "topic VARCHAR(500), subject VARCHAR(500), question VARCHAR(2000), answer VARCHAR(2000), num_times_referred_to INT, "+
             "follow_up_number INT, endorsed INT, PRIMARY KEY(question_number, follow_up_number))")

    fields = [] 
    rows = [] 
    
    # reading csv file 
    with open(filename, 'r', encoding="utf8") as csvfile: 
        # creating a csv reader object 
        csvreader = csv.reader(csvfile) 
        
        # extracting field names through first row 
        fields = next(csvreader) 
    
        # extracting each data row one by one 
        for row in csvreader: 
            rows.append(row) 
    
        curr_question = ""
        curr_text = ""
        curr_topic = ""
        curr_folder = ""
        curr_answer = ""
        curr_number = 0
        curr_follow_up = 0
        endorsed = 0
        
        # This will help us take the most recent version because it always comes first
        already_filled = 0
        for row in rows[:]: 
            # parsing each column of a row 
            for col,field in zip(row, fields): 
                if(field == "Post Number" and curr_number != int(col)):
                    if(curr_question != "" and curr_answer != ""):
                        sql = "INSERT INTO CIS120 (question_number, subject, topic, question, answer, num_times_referred_to, "\
                        "follow_up_number, endorsed) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)" 
                        val = (int(curr_number), curr_folder, curr_topic, curr_question, curr_answer, int(0), int(curr_follow_up), int(endorsed))
                        myDB.execute(sql, val)
                    curr_number = int(col)
                    curr_follow_up = 0
                    curr_question = ""
                    curr_answer = ""
                    curr_topic = ""
                    endorsed = 0

                elif(field == "Submission HTML Removed"): #the question could also be in subject
                    curr_text = col
                    
                elif(field == "Subject"): #We want to check if this is actually the question eventaully
                    curr_topic = col
                    
                elif(field == "Folders"):
                    curr_folder = col
                    
                elif(field == "Endorsed by Instructor"):
                    if(col == "TRUE"):
                        endorsed = 1
                    else:
                        endorsed = 0
                    
                elif(field == "Part of Post"):
                    if(col == "started_off_question"):
                        if(already_filled != 1):
                            curr_question = curr_text
                        alread_filled = 0
                    elif(col == "updated_question"):
                        # update question entry to post and follow up numbers
                        if(already_filled != 1):
                            curr_question = curr_text
                            already_filled = 1
                            
                    elif(col == "updated_i_answer"):
                        # update last entry to the post and follow up number
                        # what if it was appended? how do we update just the end?
                        if(already_filled != 1):
                            curr_answer = curr_answer + "\n" + curr_text
                            already_filled = 1
                        endorsed = 1
                    elif(col == "started_off_i_answer"):
                        if(already_filled != 1):
                            curr_answer = curr_answer + "\n" + curr_text
                        alread_filled = 0
                        endorsed = 1
                        
                    elif(col == "updated_s_answer"):
                        # update last entry to the post and follow up number
                        # what if it was appended? how do we update just the end?
                        if(already_filled != 1):
                            curr_answer = curr_answer + "\n" + curr_text
                            already_filled = 1
                    elif(col == "started_off_s_answer"):
                        # append to answer - if it was previously endorsed and were appending should we keep it endorsed?
                        if(already_filled != 1):
                            curr_answer = curr_answer + "\n" + curr_text
                        alread_filled = 0
                        
                    elif(col == "followup"):
                        # new entry for the new followup question 
                        if(curr_question != ""):
                            sql = "INSERT INTO CIS120 (question_number, subject, topic, question, answer, num_times_referred_to, "\
                            "follow_up_number, endorsed) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)" 
                            val = (int(curr_number), curr_folder, curr_topic, curr_question, curr_answer, int(0), int(curr_follow_up), int(endorsed))
                            myDB.execute(sql, val)
                            curr_question = ""
                            curr_answer = ""
                            endorsed = 0
                            
                        curr_follow_up = curr_follow_up + 1
                        curr_question = curr_text
                    elif(col == "reply_to_followup"):
                        curr_answer = curr_answer + "\n" + curr_text
    
    
if __name__ == "__main__":
    create_db()

