class Node:

    def __init__(self, key, raw_question, shortened_question, reference, answer):
        self.key = key # Type {question number, follow up}
        self.raw_question = raw_question 
        self.shortened_question = shortened_question
        self.reference = reference # Question number
        self.answer = answer
    


    
