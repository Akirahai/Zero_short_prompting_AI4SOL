from api.llm import get_completion_Groq
import json
import numpy as np
import matplotlib.pyplot as plt
import json
import pandas as pd
from docx import Document
import re
import os


def get_all_kc(df, grade):
    filtered_df = df[(df['Grade'] == grade)]
    subtopics_des = {}
    subtopic_list = []
    for _, row in filtered_df.iterrows():
        subtopics_des[row["Full Code"]] = row["Description"]
        subtopic_list.append(row["Full Code"])
    
    return subtopic_list, subtopics_des



def load_docx_as_text(file_path):
    doc = Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        
        full_text.append(para.text)
    return '\n'.join(full_text)


def generate_descriptions(topic_dict):
    full_des = {}
    full_list = []
    for topic, subtopics in topic_dict.items():
        subtopics_sentence = ', '.join(subtopics[:-1]) + ', and ' + subtopics[-1] if len(subtopics) > 1 else subtopics[0]
        description = f"This topic focuses on {subtopics_sentence.lower()}."
        
        full_des[topic] = description
        
        full_list.append(f"{topic}")

    return full_list, full_des


def get_subtopics(df, grade, subject):
    
    filtered_df = df[(df['Grade'] == grade) & (df['Subject'] == subject)]
    
    # Create a dictionary with subtopics and their descriptions
    subtopics_des = {}
    subtopic_list = []
    for _, row in filtered_df.iterrows():
        subtopics_des[row["Full Code"]] = row["Description"]
        subtopic_list.append(row["Full Code"])
    
    return subtopic_list, subtopics_des


# Description of KC_classification_Ver1
class KC_classification_Ver1:
    
    def __init__(self, question, solution, step, model, file_path_grade, notation_path):
        self.question = question
        self.solution = solution
        self.step = step
        self.model = model
        
        self.Grade = None
        
        # file_path_grade = 'api/common_core_data/Knowledge_Base/Data_grade/grade_dict.json'
        
        # file_path_grade = os.path.join(os.getcwd(), file_path_grade)
        
        with open(file_path_grade, 'r') as file:
            self.grade_dict = json.load(file)
        
        
        # notation_path = 'api/common_core_data/Knowledge_Base/Coherence_map_Hai.csv'
        # notation_path = os.path.join(os.getcwd(), notation_path)
        self.notation_df = pd.read_csv(notation_path, header=0)
        
    
    # Get the grade level of the question for the next step
    def get_Grade(self,):
        sys_message = f"""
        You are a professional teacher adhering to the Common Core standards, teaching Mathematics to students from Grade 1 to Grade 6. \
        Your task is to identify the minimum grade level required to answer the given question.

        Below is the description of each grade level:

        Grade 1: {self.grade_dict['1']} 
        Grade 2: {self.grade_dict['2']} 
        Grade 3: {self.grade_dict['3']}
        Grade 4: {self.grade_dict['4']}
        Grade 5: {self.grade_dict['5']}
        Grade 6: {self.grade_dict['6']}

        You will be provided with a question, and you need to determine the appropriate grade level for that question.
        
        Remember that the students needs to be at least at that grade level to answer the question.

        Provide the output in the format as "Grade X".
        
        Example:

        user: question....

        output: Grade 1
        
        """

        content = f"""
        Question: {self.question}
        Solution: {self.solution}
        """
        
        messages = [{"role": "system", "content": sys_message},
                    {"role": "user", "content": content}]
        
        response = get_completion_Groq(messages, self.model)
        reply = response.choices[0].message.content
        
        grade_level = re.findall(r'Grade \d+', reply)
        grade_level = grade_level[0].split()[1]
        grade_level = int(grade_level)
        self.Grade = grade_level
        
        return self.Grade
    
    # # Check the knowledge components required to answer the question from grade 1 to current grade
    # def get_kc(self):
    #     while self.Grade is None:
    #         try:
    #             grade = self.get_Grade()
    #             grade_level = grade.split()[1]
    #             self.Grade = grade_level
    #         except (ValueError, IndexError) as e:
    #             print(f"Error evaluating grade: {e}. Retrying...")
    #             self.Grade = None
        
        
    #     file_path = 'common_core_data/Knowledge_Base/Guideline.docx'
        
    #     guidance = load_docx_as_text(file_path)
        
    #     # Get all kcs from grade 1 to current grade
    #     full_kc_list = [] 
    #     full_kc_des = {}
        
    #     # Take the previous and next grade level
    #     if int(grade_level) == 1:
    #         start_grade = 1
    #     else:
    #         start_grade = int(grade_level) - 1
            
    #     for i in range(start_grade,int(grade_level)+1):
    #         kc_list, kc_des = get_all_kc(self.notation_df, i)
    #         full_kc_list.extend(kc_list)
    #         full_kc_des.update(kc_des)
         
        
    #     # Change to more beautiful json type file
    #     full_kc_des_json = json.dumps(full_kc_des, indent=4)

    #     print(kc_list)
                
    #     sys_message = f"""
    #         You are a professional teacher adhering to the Common Core standards, teaching Mathematics to students from Grade 1 to Grade 6. \
    #         Your task is to identify the knowledge components required to answer the given question for student at or below Grade {grade_level}. 
            
    #         Below is the description of each knowledge components from Grade {start_grade} to Grade {grade_level}:
            
    #         {full_kc_des_json}
            
    #         Provide the output in the format as "Name of Knowledge Component" from the list {kc_list}.
            
    #         Example:

    #         user: question...

    #         output: Name of Knowledge Component

    #         """
        
        
    #     content = f"""
    #     Question: '{self.question}'
    #     Solution: '{self.solution}'
    #     """
    #     messages = [{"role": "system", "content": sys_message},
    #                 {"role": "user", "content": content}]
        
    #     response = get_completion_Groq(messages, self.model)
    #     reply = response.choices[0].message.content
        
    #     print(reply)
        
    #     kc = reply
        
    #     return grade_level, kc
    
    
    def get_list_kcs(self,):
        
        if self.Grade is None:
            self.get_Grade()

        full_kc_list = [] 
        full_kc_des = {}
        
        # Take the previous and next grade level
        if int(self.Grade) == 1:
            start_grade = 1
        else:
            start_grade = int(self.Grade) - 1
            
        # for i in range(start_grade,int(self.Grade)+1):
        #     kc_list, kc_des = get_all_kc(self.notation_df, i)
        #     full_kc_list.extend(kc_list)
        #     full_kc_des.update(kc_des)
        
        full_kc_list, full_kc_des = get_all_kc(self.notation_df, int(self.Grade))
        # Change to more beautiful json type file
        full_kc_des_json = json.dumps(full_kc_des, indent=4)
        
        
        
        sys_message = f"""
            You are a professional teacher adhering to the Common Core standards, teaching Mathematics to students from Grade 1 to Grade 6. \
            Your task is to identify the knowledge components required to answer the given question for student at or below Grade {self.Grade}. 
            
            Below is the description of each knowledge components of Grade {self.Grade}:
            
            {full_kc_des_json}
            
            Provide relevant knowledge components (max: 3) required to answers the given question from the list {full_kc_list}.
            
            Here are some samples:

            Ques: question...

            output: Name of Knowledge Component

            """
            
        content = f"""
        Question '{self.question}'
        Solution '{self.solution}'
        """
        
        messages = [{"role": "system", "content": sys_message},
                    {"role": "user", "content": content}]
        
        response = get_completion_Groq(messages, self.model)
        reply = response.choices[0].message.content
        
        kcs = re.findall(r'\d+\.\w+\.\w+\.\d+', reply)

        
        return self.Grade, reply, kcs
        














class KC_classification_Ver2:
    
    def __init__(self, question, solution, step, model):
        self.question = question
        self.solution = solution
        self.step = step
        self.model = model
        
        # Descriptions of each grade level
        file_path_grade = 'api/common_core_data/Knowledge_Base/Data_grade/grade_dict.json'
        
        with open(file_path_grade, 'r') as file:
            self.grade_dict = json.load(file)
        
        # Descriptions of knowledge components
        notation_path = 'api/common_core_data/Knowledge_Base/Coherence_map_Hai.csv'

        self.notation_df = pd.read_csv(notation_path, header=0)
        
        # Descriptions of each topics of grade
        file_path_grade_des = 'api/common_core_data/Knowledge_Base/Data_grade/grade_des_dict.json'

        with open(file_path_grade_des, 'r') as file:
            self.grade_des_dict = json.load(file)
        
        
        
    
    def get_Grade(self,):
        sys_message = f"""
        You are a professional teacher adhering to the Common Core standards, teaching Mathematics to students from Grade 1 to Grade 6. \
        Your task is to identify the minimum grade level required to answer the given question.

        Below is the description of each grade level:

        Grade 1: {self.grade_dict['1']} 
        Grade 2: {self.grade_dict['2']} 
        Grade 3: {self.grade_dict['3']}
        Grade 4: {self.grade_dict['4']}
        Grade 5: {self.grade_dict['5']}
        Grade 6: {self.grade_dict['6']}

        You will be provided with a question, and you need to determine the appropriate grade level for that question.
        
        Remember that the students needs to be at least at that grade level to answer the question.

        Provide the output in the format as "Grade X".
        
        Example:

        user: question....

        output: Grade 1
        """

        
        messages = [{"role": "system", "content": sys_message},
                    {"role": "user", "content": self.question}]
        
        response = get_completion_Groq(messages, self.model)
        reply = response.choices[0].message.content
        
        print(reply)
        return reply
    
    
    def get_grade_components(self):
        grade = None
        while grade is None:
            try:
                grade = self.get_Grade()
                grade_level = grade.split()[1]
            except (ValueError, IndexError) as e:
                print(f"Error evaluating grade: {e}. Retrying...")
                grade = None
        
        
        full_list_grade, full_des_grade = generate_descriptions(self.grade_des_dict[grade_level])
        
        full_des_grade_json = json.dumps(full_des_grade, indent=4)
        
        file_path = 'common_core_data/Knowledge_Base/Guideline.docx'
        
        guidance = load_docx_as_text(file_path)

                
        sys_message = f"""
            You are a professional teacher adhering to the Common Core standards, teaching Mathematics to students from Grade 1 to Grade 6. \
            Your task is to identify the knowledge components required to answer the given question for student at or below Grade {grade_level}. 
            Below is the guidance that you need to follow while identifying the knowledge components of the question:
            
            {guidance}

            Below is the description of each topic at Grade {grade_level}:
            
            {full_des_grade_json}

            You will be provided with a question, and you need to determine the appropriate topic for that question.

            Provide the output in the format as "Name of topic" from the list {full_list_grade}.
            
            Example:

            user: question....

            output: Name of topic
            """
        
        messages = [{"role": "system", "content": sys_message},
                    {"role": "user", "content": self.question}]
        
        response = get_completion_Groq(messages, self.model)
        reply = response.choices[0].message.content
        
        print(reply)
        
        topic = reply
        
        return grade_level, topic
    
    def get_kc(self):
        
        grade, topic = self.get_grade_components()
        kc_list, kc_des = get_subtopics(self.notation_df, int(grade), topic)
        
        kc_des_json = json.dumps(kc_des, indent=4)
        
        # print(kc_des_json)
        
        # print(kc_list)
        
        sys_message = f"""
            You are a professional teacher adhering to the Common Core standards, teaching Mathematics to students from Grade 1 to Grade 6. \
            Your task is to identify the subtopic required to answer the given question at Grade {grade} and topic {topic}.

            Below is the list of subtopics for the topic {topic} at Grade {grade}:
            
            {kc_des_json}

            You will be provided with a question, and you need to determine the appropriate knowledge components at Grade {grade} for that question.

            
            Provide the output in the format as "Name of Knowledge Component" from the list {kc_list}.
            
            Example:

            user: question...

            output: Name of KC
            
            """
        
        messages = [{"role": "system", "content": sys_message},
                    {"role": "user", "content": self.question}]
        
        response = get_completion_Groq(messages, self.model)
        reply = response.choices[0].message.content
        
        print(reply)
        
        kcs = re.findall(r'\d+\.\w+\.\w+\.\d+', reply)
        
        return kcs
        
        
# class KC_classification_Ver3:
    
#     def __init__(self, question, solution, step, model):
#         self.question = question
#         self.solution = solution
#         self.step = step
#         self.model = model
        
#         # Descriptions of each grade level
#         file_path_grade = 'Data_grade/grade_dict.json'

#         with open(file_path_grade, 'r') as file:
#             self.grade_dict = json.load(file)
        
#         # Descriptions of knowledge components
#         notation_path = 'common_core_data/Coherence_map_Hai.csv'

#         self.notation_df = pd.read_csv(notation_path, header=0)
        
        

    
#     # Get the grade level of the question for the next step
#     def get_Grade(self,):
#         sys_message = f"""
#         You are a professional teacher adhering to the Common Core standards, teaching Mathematics to students from Grade 1 to Grade 6. \
#         Your task is to identify the minimum grade level required to answer the given question.

#         Below is the description of each grade level:

#         Grade 1: {self.grade_dict['1']} 
#         Grade 2: {self.grade_dict['2']} 
#         Grade 3: {self.grade_dict['3']}
#         Grade 4: {self.grade_dict['4']}
#         Grade 5: {self.grade_dict['5']}
#         Grade 6: {self.grade_dict['6']}

#         You will be provided with a question and the solution of the problems, and you need to determine the appropriate grade level for that question.
        
#         Remember that the students needs to be at least at that grade level to answer the question.

#         Provide the output in the format as "Grade X".
        
#         Example:

#         user: question....

#         output: Grade 1
#         """

#         content = f"""
#         Question: {self.question}
#         Solution: {self.solution}
#         """
        
#         messages = [{"role": "system", "content": sys_message},
#                     {"role": "user", "content": content}]
        
#         response = get_completion_Groq(messages, self.model)
#         reply = response.choices[0].message.content
        
#         print(reply)
#         return reply
    
#     # Check the knowledge componets required to answer the question from grade 1 to current grade
#     def get_kc(self):
#         grade = None
#         while grade is None:
#             try:
#                 grade = self.get_Grade()
#                 grade_level = grade.split()[1]
#             except (ValueError, IndexError) as e:
#                 print(f"Error evaluating grade: {e}. Retrying...")
#                 grade = None
        
        
#         file_path = 'common_core_data/Guideline.docx'
        
#         guidance = load_docx_as_text(file_path)
        
#         # Get all kcs from grade 1 to current grade
#         full_kc_list = [] 
#         full_kc_des = {}
#         for i in range(1,int(grade_level)+1):
#             kc_list, kc_des = get_all_kc(self.notation_df, i)
#             full_kc_list.extend(kc_list)
#             full_kc_des.update(kc_des)
        
#         # Change to more beautiful json type file
#         full_kc_des_json = json.dumps(full_kc_des, indent=4)
        
                
#         sys_message = f"""
#             You are a professional teacher adhering to the Common Core standards, teaching Mathematics to students from Grade 1 to Grade 6. \
#             Your task is to identify the knowledge components required to answer the given question for student at or below Grade {grade_level}. 
#             Below is the guidance that you need to follow while identifying the knowledge components of the question:
            
#             ''{guidance}''

#             Below is the description of each knowledge components from Grade 1 to Grade {grade_level}:
            
#             {full_kc_des_json}

#             You will be provided with a question, with its solution and the step that you need to identify the \
#             knowledge component following the guidance.
            
#             Each step can have more than one knowledge component, but do not provide more than two knowledge components for each step..

#             Provide the output in the format as "Name of Knowledge Component" from the list {full_kc_list}. You do not need to solve the question.
            
#             EXAMPLE:

#             user: Question: 'Albert is wondering how much pizza he can eat in one day. He buys 2 large pizzas and 2 small pizzas. A large pizza has 16 slices and a small pizza has 8 slices. If he eats it all, how many pieces does he eat that day?'
#                 Solution: 'He eats 32 from the largest pizzas because 2 x 16 = <<2*16=32>>32\nHe eats 16 from the small pizza because 2 x 8 = <<2*8=16>>16\nHe eats 48 pieces because 32 + 16 = <<32+16=48>>48\n#### 48'
#                 Step: '<<2*16=32>>'
                  
#             output: 3.OA.A.3
            
#             user: Question: 'Weng earns $12 an hour for babysitting. Yesterday, she just did 50 minutes of babysitting. How much did she earn?'
#                 Solution: 'Weng earns 12/60 = $<<12/60=0.2>>0.2 per minute.\nWorking 50 minutes, she earned 0.2 x 50 = $<<0.2*50=10>>10.\n#### 10'
#                 Step: '<<12/60=0.2>>'
                
#             output: 4.MD.A.2, 4.NF.C.6
            
#             """
        
        
        
#         content = f"""
#         Question: '{self.question}'
#         Solution: '{self.solution}'
#         Step: '{self.step[0]}'
#         """
        
#         reply_dict = {} 
        
#         messages = [{"role": "system", "content": sys_message}]
        
#         for i in range(len(self.step)):
#             content = f"""
#             Question: {self.question}
#             Solution: {self.solution}
#             Step: {self.step[i]}
#             """
            
#             messages.append({"role": "user", "content": content})
            
#             response = get_completion_Groq(messages, self.model)
#             reply = response.choices[0].message.content
            
#             # messages.append({"role": "assistant", "content": reply})
            
#             messages = [{"role": "system", "content": sys_message}]
            
            
#             reply_dict[self.step[i]] = reply
        
#         # kc_dict_json = json.dumps(reply_dict, indent=4)
        
#         return grade_level, reply_dict
        
        
        