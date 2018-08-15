import os
import nltk
import random
import configparser
from stanfordcorenlp import StanfordCoreNLP
from slacker import Slacker
from nltk.corpus import wordnet
from chat_bot_server_dir.project_parser import project_parser

# nltk.download('wordnet')

give_thanks = ["Thank you! Have a good day!", "That's good! Thank you!", "That is great! Thank you!", "Nice! Thank you!", "Ok. Thank you!"]
ignore_file = ["Okay! I'll ignore that file", "Okay! Ignore list appened!", "Okay! Ignore file registered!", "Good! I'll ignore that file", "Good! Ignore list appened!", "Good! Ignore file registered!"]

def load_token() :
    if not os.path.isfile("bot_server_config.ini") :
        print("ERROR :: There is no bot_server_config.ini")
        exit(2)
    else :
        config = configparser.ConfigParser()
        config.read("bot_server_config.ini")
        try :
            token=config["SLACK"]["TOKEN"]
        except :
            print("ERROR :: It is bot_server_config.ini")
            exit(2)
    return token

token = load_token()
slack = Slacker(token)

def get_slack_name_list():
    try:
        user_list = list()
        # Get users list
        response = slack.users.list()
        users = response.body['members']
        for user in users:
            if user.get('profile').get('display_name') != '':
                user_list.append(user.get('profile').get('display_name'))
            else:
                user_list.append(user.get('profile').get('real_name'))
    except KeyError as ex:
        print('Invalid key : %s' % str(ex))
    return user_list

slack_name_list = get_slack_name_list()
project_structure = project_parser('UCNLP', 'client')

def lemma(keyword):
    lemmatizer = nltk.WordNetLemmatizer()
    org_wrd = lemmatizer.lemmatize(keyword)
    return org_wrd

def find_syn(word):
    synonyms = []

    for syn in wordnet.synsets(word):
        for l in syn.lemmas():
            synonyms.append(l.name())
    return set(synonyms)

def give_intent_return_message(sentence):
    nlp = StanfordCoreNLP('http://localhost', port=9000)

    word_tokenize_list = nlp.word_tokenize(sentence)
    dependency_parse_list = nlp.dependency_parse(sentence)

    dependency_catch_list = ["dobj", "nmod", "xcomp", "nsubj"]

    for dependency_pair in dependency_parse_list:
        if dependency_pair[0] in dependency_catch_list:
            pair_set1 = find_syn(word_tokenize_list[dependency_pair[1] - 1])
            pair_set2 = find_syn(word_tokenize_list[dependency_pair[2] - 1])
            if "solve" in pair_set1 or "solve" in pair_set2:
                return give_thanks[random.randint(0, len(give_thanks)-1)]
            elif "ignore" in pair_set1 or "ignore" in pair_set2:
                return ignore_file[random.randint(0, len(ignore_file)-1)]
            elif "location" in pair_set1 or "location" in pair_set2:
                return "oh that location is function_parsing_test 16 line."
            elif "conflict" in pair_set1 or "conflict" in pair_set2:
                return "You and jc's conflict size is 1."
            elif ("size" in pair_set1 or "size" in pair_set2) and "working" in sentence:
                return "jc's working size is 1."
            elif ("recommend" in pair_set1 or "recommend" in pair_set2) and "conflict" in sentence:
                return "You edited 1 line, but js worked 3line. I think you should stop."
            elif "status" in pair_set1 or "status" in pair_set2:
                return "jc is working on function_parsing_test 16 line."

    # print ('Tokenize:', word_tokenize_list)
    # print ('Part of Speech:', nlp.pos_tag(sentence))
    # print ('Named Entities:', nlp.ner(sentence))
    # print ('Constituency Parsing:', nlp.parse(sentence))
    # print ('Dependency Parsing:', dependency_parse_list)

    nlp.close()
