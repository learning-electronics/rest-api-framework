import subprocess
import docx2python 
import re
import copy
import os
from PIL import Image
from os.path import realpath,dirname,join

project_path = dirname(dirname(dirname(realpath(__file__))))

RULE_CHOICES = ( ("A", "Ampere"), ("V", "Volt"), ("W", "Watt"), ("Ohm", "Ohm"), ("None", "Nenhuma") )


def get_exercise_dict(path_to_file,):
    #"20211124_BD_de_Exercicios_DC.doc"
    if path_to_file.endswith(".doc"):
        subprocess.call(['soffice', '--headless', '--convert-to', 'docx', '--outdir', project_path+"/api/media/", project_path+path_to_file])
        path_to_file = path_to_file.replace(".doc", ".docx")

    raw_data = []
    #[doc][pagina][linha][caracter]
    os.mkdir(project_path+ path_to_file.split('.')[0]+"_media")
    for doc in docx2python.docx2python(project_path+path_to_file, project_path+path_to_file.split('.')[0]+"_media", html=True).body:
        for table in doc:
            for row in table:
                row = [x.replace('\n', '').replace('\t', '') for x in row if x and (not x.isspace() and x !='<h1></h1>')] # remove empty cells
                raw_data=row

    exercises_data=[] 
    exercise_dict={}
    while raw_data:
        string = raw_data.pop(0)
        exercise_strings = [] 
        if '<h1>' and '</h1>' in string and string!='<h1></h1>':
            exercise_strings.append(string) 
            while raw_data and not (('<h1>' and '<\h1>' in raw_data[0]) or ('<h1>' and '</h1>' in raw_data[0])):
                exercise_strings.append(raw_data.pop(0))
            
            #get image name
            for i in range(len(exercise_strings)):
                if exercise_strings[i] and (('.png' or '.wmf') and '----') in exercise_strings[i]:
                    tmp = [x for x in exercise_strings[i].split('----') if x !='']
                    if len(tmp)>1:
                        for s in tmp:
                            if (('.png' or '.wmf') and 'media/') in s: 
                                exercise_dict['img'] = s#.replace('.xmf', '.png')
                                tmp.pop(tmp.index(s))
                                exercise_strings[i]= ''.join(tmp)
                                break
                    else:
                        exercise_dict['img'] = tmp[0]#.replace('.xmf', '.png')
                        exercise_strings.pop(i)
                    break

            #get themes
            exercise_dict['theme'] = exercise_strings.pop(0).replace('<h1>', '').replace('</h1>', '')

            #get half question
            question_txt = ''
            regex_pattern = re.compile(r'[0-9]+\)')
            while exercise_strings and not (regex_pattern.search(exercise_strings[0]) and exercise_strings[0][0].isdigit()):
                question_txt += exercise_strings.pop(0)

            while True:
                tmp = exercise_strings.pop(0).split(')',1)
                exercise_dict['question'] = question_txt +'. '+ tmp[1]
                ans_array = exercise_strings.pop(0).replace('R:', '').split(';')
                for i in range(len(ans_array)):
                    ans = ans_array[i].lstrip()
                    if ans.startswith('#') and ans.endswith('#'):        
                        exercise_dict['correct'] = ans.replace('#', '')
                        ans_array.pop(i)
                        break

                exercise_dict['ans1'] = ans_array.pop(0).lstrip()
                exercise_dict['ans2'] = ans_array.pop(0).lstrip()
                exercise_dict['ans3'] = ans_array.pop(0).lstrip()

                exercises_data.append(copy.deepcopy(exercise_dict))

                if exercise_strings:
                    exercise_dict.pop('correct', None)
                    exercise_dict.pop('ans1', None)
                    exercise_dict.pop('ans2', None)
                    exercise_dict.pop('ans3', None)
                    exercise_dict.pop('question', None)
                elif raw_data and (('<h1>' and '<\h1>' in raw_data[0]) or ('<h1>' and '</h1>' in raw_data[0])):
                    exercise_dict={}
                    break

                if not raw_data and not exercise_strings:
                    break

    os.remove(project_path + path_to_file)
    return exercises_data

#Convert .xmf images to .png
def convert_xmf_to_png(folder_path):
    for file in os.listdir(folder_path):
        print(file)
        if file.endswith(".wmf"):
            
            print(Image.open(folder_path+file).save(folder_path+file.split('.')[0]+".png"))
            os.remove(file)

if __name__ == '__main__':
    get_exercise_dict("20211124_BD_de_Exercicios_DC.doc")