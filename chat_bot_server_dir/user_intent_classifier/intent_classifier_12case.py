import os
import nltk
import random
import configparser
from stanfordcorenlp import StanfordCoreNLP
from slacker import Slacker
from nltk.corpus import wordnet
from chat_bot_server_dir.project_parser import project_parser
<<<<<<< Updated upstream
from pathlib import Path

=======
import chat_bot_server_dir.user_intent_classifier.intent_classifier as intent_classifier
>>>>>>> Stashed changes

#nltk.download('wordnet')

give_thanks = ["Thank you! Have a good day!", "That's good! Thank you!", "That is great! Thank you!", "Nice! Thank you!", "Ok. Thank you!"]
ignore_file = ["Okay! I'll ignore that file", "Okay! Ignore list appended!", "Okay! Ignore file registered!", "Good! I'll ignore that file", "Good! Ignore list appened!", "Good! Ignore file registered!"]
location_list = ["Where","where","location"]

def load_token() :
    bot_server_config_path = os.path.join(Path(os.getcwd()).parent, "bot_server_config.ini")

    if not os.path.isfile(bot_server_config_path) :
        print("ERROR :: There is no bot_server_config.ini")
        exit(2)
    else :
        config = configparser.ConfigParser()
        config.read(bot_server_config_path)
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
    pos_tag_list = nlp.pos_tag(sentence)
    parse_list = nlp.parse(sentence)

<<<<<<< Updated upstream
    dependency_catch_list = ["dobj", "nmod", "xcomp", "nsubj"]

    print ('Tokenize:', word_tokenize_list)
    print ('Part of Speech:', nlp.pos_tag(sentence))
    #print ('Named Entities:', nlp.ner(sentence))
    print ('Constituency Parsing:', nlp.parse(sentence))
    print ('Dependency Parsing:', dependency_parse_list)

    count = 1
    for dependency_pair in dependency_parse_list:
        print(count)
        count += 1
        if dependency_pair[0] in dependency_catch_list:
            pair_set1 = find_syn(word_tokenize_list[dependency_pair[1] - 1])
            pair_set2 = find_syn(word_tokenize_list[dependency_pair[2] - 1])
            #case1 : solve
            if "solve" in pair_set1 or "solve" in pair_set2:
                return give_thanks[random.randint(0, len(give_thanks)-1)]
            #case2 : ignore file
            elif "ignore" in pair_set1 or "ignore" in pair_set2:
                return ignore_file[random.randint(0, len(ignore_file)-1)]
            #case3 : conflict location
            elif "location" in pair_set1 or "location" in pair_set2:
                return "oh that location is function_parsing_test 16 line."
            # elif "where" or "Where" in sentence:
            #     return "oh that location is function_parsing_test 17 line."

            #case4-1 : conflict size
            elif "conflict" in pair_set1 or "conflict" in pair_set2:
                return "You and jc's conflict size is 1."
            #case4-2 : working size?
            elif ("size" in pair_set1 or "size" in pair_set2) and "working" in sentence:
                return "jc's working size is 1."
            #case5 : recommendation
            elif ("recommend" in pair_set1 or "recommend" in pair_set2) and "conflict" in sentence:
                return "You edited 1 line, but js worked 3line. I think you should stop."
            #case7 : other user working status
            elif "status" in pair_set1 or "status" in pair_set2:
                return "jc is working on function_parsing_test 16 line."



    nlp.close()

# sentence1 = "We solved, thank you!" #solve
sentence2 = "I want to ignore file1.py." #ignore
sentence3 = "Where did conflict happen in file1.py between me and jc?" #conflict location
sentence4 = "I want to know how many lines the conflict exist at file1.py." #conflict size
sentence5 = "Can you recommend how I can solve conflict in File1.py?" #recommendation
sentence6 = "Can you check if there is a conflict in File1.py?" #Check the file if it generates conflict or not
sentence7 = "I want to know jc's working status." #working status
sentence8 = "Can I check the code history of File1.py?" #code history
sentence9 = "Can you lock File1.py?" #Lockfile
sentence10 = "Can you send this message to general channel?"#Announce
sentence11 = "Can you send direct message to user2 that we should solve the conflict in File1.py?" #Message

print(give_intent_return_message(sentence7))
=======
    print('Tokenize:', word_tokenize_list)
    print('Part of Speech:', pos_tag_list)
    print('Constituency Parsing:', parse_list)
    print('Dependency Parsing:', dependency_parse_list)

    # Case of question
    if intent_classifier.require_something_sentence(sentence)==1:
        # Intent words for analyzing the sentence
        intent_word_list = []
        # Questions starting with 5 w and 1 h (Direct Questions)
        if "SBARQ" in parse_list:
            # dependency_catch_list = ["advmod" , "nsubj", "dobj"]
            for dependency_pair in dependency_parse_list:
                if dependency_pair[0] == 'advmod':
                    pair_set1 = find_syn(lemma(word_tokenize_list[dependency_pair[2] - 1]))
                    intent_word_list.append(pair_set1)
                if dependency_pair[0] == 'nsubj':
                    pair_set2 = find_syn(lemma(word_tokenize_list[dependency_pair[2] - 1]))
                    pair_set3 = find_syn(lemma(word_tokenize_list[dependency_pair[1] - 1]))
                    intent_word_list.append(pair_set2)
                    intent_word_list.append(pair_set3)
                if dependency_pair[0] == 'dobj':
                    pair_set4 = find_syn(lemma(word_tokenize_list[dependency_pair[1] - 1]))
                    intent_word_list.append(pair_set4)
                else:
                    continue
        # Questions starting with verb or modal (Inverted/Indirect Questions)
        elif "SQ" in parse_list:
            # dependency_catch_list = ["nsubj", "dobj"]
            message_hint_words = {"chat", "talk", "tell", "speak", "say"}
            for dependency_pair in dependency_parse_list:
                # when the user wants to send message to other users
                if dependency_pair[0] == 'nsubj' and word_tokenize_list[dependency_pair[1]-1] in message_hint_words:
                    pass
                    # message_sentence = 'after that'
                if dependency_pair[0] == 'nsubj':
                    pair_set1 = find_syn(lemma(word_tokenize_list[dependency_pair[2] - 1]))
                    pair_set2 = find_syn(lemma(word_tokenize_list[dependency_pair[1] - 1]))
                    intent_word_list.append(pair_set1)
                    intent_word_list.append(pair_set2)
                if dependency_pair[0] == 'dobj':
                    pair_set3 = find_syn(lemma(word_tokenize_list[dependency_pair[2] - 1]))
                    intent_word_list.append(pair_set3)
                else:
                    continue

    # for dependency_pair in dependency_parse_list:
    #     if dependency_pair[0] in dependency_catch_list:
    #         pair_set1 = find_syn(word_tokenize_list[dependency_pair[1] - 1])
    #         pair_set2 = find_syn(word_tokenize_list[dependency_pair[2] - 1])
    #         if "solve" in pair_set1 or "solve" in pair_set2:
    #             return give_thanks[random.randint(0, len(give_thanks)-1)]
    #         elif "ignore" in pair_set1 or "ignore" in pair_set2:
    #             return ignore_file[random.randint(0, len(ignore_file)-1)]
    #         elif "location" in pair_set1 or "location" in pair_set2:
    #             return "oh that location is function_parsing_test 16 line."
    #         elif "conflict" in pair_set1 or "conflict" in pair_set2:
    #             return "You and jc's conflict size is 1."
    #         elif ("size" in pair_set1 or "size" in pair_set2) and "working" in sentence:
    #             return "jc's working size is 1."
    #         elif ("recommend" in pair_set1 or "recommend" in pair_set2) and "conflict" in sentence:
    #             return "You edited 1 line, but js worked 3line. I think you should stop."
    #         elif "status" in pair_set1 or "status" in pair_set2:
    #             return "jc is working on function_parsing_test 16 line."

    nlp.close()

give_intent_return_message("Can you talk to user2 that I will do it?")
