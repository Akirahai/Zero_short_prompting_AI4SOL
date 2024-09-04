from libs import *
from api import Full_API_models
if os.getcwd().split('\\')[-1] == 'api':
    os.chdir('..')
    print(os.getcwd())
    
    
file_path_grade = 'common_core_data/Knowledge_Base/Data_grade/grade_dict.json'
notation_path = 'common_core_data/Knowledge_Base/Coherence_map_Hai.csv'




if __name__== "__main__":
    
    # Setting Up
    model_list  = ['gemma-7b-it', 'mixtral-8x7b-32768', 'llama3-70b-8192', 'llama3-8b-8192', 'gpt-3.5-turbo']
    model = model_list[4]
    data_file = 'Grade_data_Train'

    kc_label_path = f'common_core_data/Data/{data_file}.csv'
    kc_label = pd.read_csv(kc_label_path, header=0)
    KC_question = {}



    for i in tqdm(range(len(kc_label))):
        if i not in KC_question.keys():
            ques = kc_label.loc[i, 'Question']
            kcs = kc_label.loc[i, 'KCs applied']
            grade_applied = kc_label.loc[i, 'Grade applied']
            
            try:
                sol = kc_label.loc[i, 'Solution']
            except:
                sol = None
                
            try:
                steps = kc_label.loc[i, 'Steps']
            except:
                steps = None
                
            Ques1 = Full_API_models.KC_classification_Ver1(ques, sol, steps, model=model, file_path_grade=file_path_grade, notation_path=notation_path)
            
            try:
                Ques1.Grade = grade_applied
                grade, full_reply, kc_list = Ques1.get_list_kcs()
                
                KC_question[i] = {'Question': ques, 'KCs applied': kcs, 'Grade': grade, 'KCs predicted': kc_list, 'Full reply': full_reply}
            
            except:
                print(f'Error at {i}')
                KC_question[i] = None
            
            # print(f'This is the {i}th question')
            # print(f'Question: {ques}')
            # print(f'KCs applied: {kcs}')
            # print(f'Grade applied: {grade_applied}')
            # print(f'Grade predicted: {grade}')
        
        
    

    # Debugging_code
    for i in tqdm(range(len(kc_label))):
        if KC_question[i] is None:
            ques = kc_label.loc[i, 'Question']
            kcs = kc_label.loc[i, 'KCs applied']
            grade_applied = kc_label.loc[i, 'Grade applied']
            
            Ques1 = Full_API_models.KC_classification_Ver1(ques, 0, 0, model=model)
            
            try:
                Ques1.Grade = grade_applied
                grade, full_reply, kc_list = Ques1.get_list_kcs()
                
                KC_question[i] = {'Question': ques, 'KCs applied': kcs, 'Grade': grade, 'KCs predicted': kc_list, 'Full reply': full_reply}
            
            except:
                print(f'Error at {i}')
                KC_question[i] = None
            
            # print(f'This is the {i}th question')
            # print(f'Question: {ques}')
            # print(f'KCs applied: {kcs}')
            # print(f'Grade applied: {grade_applied}')
            # print(f'Grade predicted: {grade}')
            
    
    # Saving the data
    kc_df = pd.DataFrame(KC_question)
    kc_df = kc_df.T
    kc_df = kc_df.reset_index(drop=True)
    kc_label['KCs predicted'] = kc_df['KCs predicted']
    kc_label['Grade'] = kc_df['Grade']
    kc_label['Full Reply'] = kc_df['Full reply']
        
    data_file = 'Grade_data_Train'
    data_file+= '_from_Grade'
    
    kc_label.to_csv(f'common_core_data/Test_Result/{data_file}/{data_file}_question_level_{model}.csv', index=False)