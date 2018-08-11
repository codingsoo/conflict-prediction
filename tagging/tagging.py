import os
from nltk.parse import stanford

os.environ['CLASSPATH']="/Users/seungeonlee/Downloads/stanford-parser-full-2017-06-09/stanford-parser.jar"
os.environ['STANFORD_MODELS']="/Users/seungeonlee/Downloads/stanford-parser-full-2017-06-09/stanford-parser-3.8.0-models.jar"

dep_parser = stanford.StanfordDependencyParser()
pos_parser = stanford.StanfordParser()

f = open("chat_text.txt","r")
sentences = f.readlines()

result = []

for i in sentences:
    parsed_sentences = dep_parser.raw_parse(i)
    dep = parsed_sentences.next()
    dep_list = list(dep.triples())

    dependency = []
    for l in dep_list:
        dependency.append([l[1],l[0][0],l[2][0]])

    nmod_list = []
    dobj_list = []


    for d in dependency:
        if d[0] == 'nmod':
            temp = []
            temp.append(d[1])
            temp.append(d[2])
            nmod_list.append(temp)
        elif d[0] == 'dobj':
            temp = []
            temp.append(d[1])
            temp.append(d[2])
            dobj_list.append(temp)

    for dl in dobj_list:
        for nl in nmod_list:
            f_list = []
            if dl[1] == nl[0]:
                f_list.append(dl[0])
                f_list.append(dl[1])
                f_list.append(nl[1])
                f_list.append(i)
                result.append(f_list)
            else:
                f_list.append("")
                f_list.append("")
                f_list.append("")
                f_list.append(i)
                result.append(f_list)
print(result)
