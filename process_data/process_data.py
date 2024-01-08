import os
import spacy
import csv
nlp = spacy.load("en_core_web_sm")

def find_root(doc):
    # 寻找中心词，和时间词
    center_word = None
    date_time_words=[]
    tokens=[]
    for token in doc:
        tokens.append(token)
    date_time_words.append([])
    j=0
    for i in range(len(tokens)):
        if tokens[i].dep_=="ROOT":
            center_word = tokens[i]
        if tokens[i].ent_type_ in ["TIME","DATE"]:
            date_time_words[j].append(tokens[i])
            if tokens[i+1].ent_type_ in ["TIME","DATE"]:
                pass
            else:#前一个是时间词，这一个不是时间词。
                date_time_words.append([])##做一个标记，把每个时间词分隔开
                j+=1
                ##date_time_words=[[twenty,years,later],[today]]#每个时间词都是一个列表
    if len(date_time_words[-1])==0:#如果最后是一个空列表，则删除
        date_time_words.pop()
    return center_word,date_time_words

def process_data_line(date_time_words,Root):
    pre_num=0
    post_num=0
    pre_MDD_sum=0
    post_MDD_sum=0
    if date_time_words!=[]:
        for word_list in date_time_words:
            l=len(word_list)##每个时间词
            total=0
            for word in word_list:
                ##找出一个词组中每一个词到中心词的距离
                distance = Root.i- word.i
                total+=distance
            average_dd=float(total/float(l))##每个时间词（词组）的平均依存距离
            if average_dd>=0:#前置时间词
                pre_num+=1
                pre_MDD_sum+=average_dd
            else:
                post_num+=1
                post_MDD_sum+=average_dd*(-1)
    return pre_num,post_num,pre_MDD_sum,post_MDD_sum



def lower_(i):##i是一个列表，内含时间词
    words=[]
    for word in i:
        print(type(word))
        if type(word.text)==str:
            word=word.text.lower()
            words.append(word)
        else:##数字
            words.append(word.text)
    words=" ".join(words)
    return words

def process_data(txt_file,time_words):
    results=[0.0 for i in range(9)]
    description=[]
    diversity=0
    for line in txt_file:#文件里的每一行
        doc = nlp(line)
        result={}
        result["DATE"]=[]
        result["TIME"]=[]
        result['ROOT']=""
        # 遍历文档中的实体
        for ent in doc.ents:
            if ent.label_ == "DATE":  # 只选择日期实体
                result["DATE"].append(ent.text)
                #print(f"日期: {ent.text, ent.text_with_ws}")
            if ent.label_ == 'TIME':
                result["TIME"].append(ent.text)
        if result["DATE"]!=[] or result["TIME"]!=[]:
            ##不等于空，则要进行后续计算
            Root,date_time_words=find_root(doc)
            pre_num,post_num,pre_MDD_sum,post_MDD_sum=process_data_line(date_time_words,Root)
            for i in date_time_words:
                i=lower_(i)
                print(i)
                time_words.append(i)###用于计算时间词频数
                if i not in description:
                    description.append(i)
                    diversity+=1##计算丰富度
            results[0]+=pre_num
            results[2]+=pre_MDD_sum
            results[3]+=post_num
            results[5]+=post_MDD_sum
        else:
            continue
    if results[0]==0 and results[3]==0:
        return 0
    results[1]=results[0]/float(results[0]+results[3])
    results[4]=results[3]/float(results[0]+results[3])
    results[6]=results[2]+results[5]
    results[7]=diversity
    results[8]=description
    return results

# 指定文件夹路径
folder_path = 'tokenized'

# 存储文件名的列表
txt_files = []
results=[]#所有文件的时间词及相关依存距离

# 使用os.scandir()获取目录条目（目的是，按顺序对文件夹中的txt文件进行处理）
with os.scandir(folder_path) as entries:
    for entry in entries:
        if entry.is_file() and entry.name.endswith('.txt'):
            txt_files.append(entry.name)
# 遍历文件夹中的每个文件
i=0
time_words=[]
for file in txt_files:
    
    if file.endswith('.txt'):
        #txt_files.append(file)#将每个txt文件的名字按顺序存储下来
        i+=1
        file_path = os.path.join(folder_path, file)
        with open(file_path, 'r', encoding='utf-8') as txt_file:
            # 处理每个文件所的数据，
            result = process_data(txt_file,time_words)
            if result!=0:
                result.insert(0,file)
                results.append(result)
            #results.append([file,result])
            #file是文档名字
    if i==100:
        break
    ##先处理前100个文件

print(results)
def sort_date_time(time_words):
    date_time={}
    for j in time_words:
        
        if not date_time.get(j):
            date_time[j]=0
        date_time[j]+=1
    sorted_date_time = dict(sorted(date_time.items(), key=lambda item: item[1], reverse=True))
    return sorted_date_time

def process_results(results):
    process_results=[["filename","preposotion_num","preposotion_ratio","preposotion_MDD_doc","postposotion_num","postposotion_ratio","postposotion_MDD_doc","MDD_doc","Diversity","Description"]]
    for result in results:

        process_results.append(result)
    return process_results

def out_csv(results):
    filename="results.csv"
    with open(filename, 'w', newline='') as csvfile:
       writer = csv.writer(csvfile)
       writer.writerows(results)

def date_time_csv(sorted_date_time):
    date_time=[]
    for k,v in sorted_date_time.items():
        data=[k,v]
        date_time.append(data)
    filename="sorted_date_time.csv"
    with open(filename, 'w', newline='') as csvfile:
       writer = csv.writer(csvfile)
       writer.writerows(date_time)
    return
sorted_date_time=sort_date_time(time_words)
results_=process_results(results)
out_csv(results_)
date_time_csv(sorted_date_time)
print(time_words)

