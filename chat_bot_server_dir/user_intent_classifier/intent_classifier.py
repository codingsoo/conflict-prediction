import spacy

from chat_bot_server_dir.user_intent_classifier.sentence_type_finder import require_something_sentence
from chat_bot_server_dir.project_parser import *
from chat_bot_server_dir.python_logic_parser import *
from chat_bot_server_dir.user_intent_classifier.sentence_type_finder import *
from chat_bot_server_dir.work_database import *


# from chat_bot_server_dir.user_intent_classifier.project_parser import *
# from chat_bot_server_dir.user_intent_classifier.python_logic_parser import *

# You can download this file : https://spacy.io/usage/vectors-similarity
nlp = spacy.load(
    '/Users/chaeyeon/Desktop/workspace/NLP/venv/lib/python3.7/site-packages/spacy/data/en_core_web_lg/en_core_web_lg-2.0.0')

# bot's feature
# 1. ignore_file : It is like gitignore. User can customize their ignore files.
# 2. lock_file : User can lock their files. If other users try to modify lock_files' related file, chatbot gives them warning.
# 3. code_history : User can ask about code who wrote.
# 4. ignore_alarm : User can ignore direct and indirect conflict.
# 5. check_conflict : Before user works, user can check if he generates conflict or not with user's working file.
# 6. working_status : User can ask about other user's working status
# 7. channel_message : User can let chatbot give message to channel.
# 8. user_message : User can let chatbot give message to other users.
# 9. recommend : User can ask recommend behavior about conflict.
# 10. user_recognize : Bot knows when user connected last time, so bot can greet person with time information. ex) It's been a while~
# 11. greeting : Bot can greet users.
# 12. complimentary_close : Bot can say good bye.
# 13. detect_direct_conflict : Bot can detect direct conflict and severity.
# 14. detect_indirect_conflict : Bot can detect indirect conflict and severity.


question_sentence_list = ["Can you not notify me about hello.py?", "Can you lock hello.py?",
                          "Can you tell me who wrote line14?", "Can you not notify me about indirect conflict?",
                          "Do you think this is gonna make a conflict?", "Can you tell me user2's working status?",
                          "Can you tell everyone that I'm working on File1.py?",
                          "Can you chat to User2 that I will check and solve the problem?",
                          "Can you recommend what should I do to fix the conflict?"]
command_sentence_list = ["Don't alert me about File1.py again.", "Lock hello.py file.", "Tell me who wrote def1().",
                         "Don't alert me about indirect conflict.",
                         "Check File1.py whether it will make conflict or not.",
                         "Tell everyone that I'm working on File1.py to conflict detect channel.",
                         "Send user2 a message that I'm working on class1.",
                         "Give me some recommendation about how to solve the conflict of File1.py."]
suggestion_sentence_list = ["You should not give me notification about File1.py", "You should lock File.py.",
                            "Sayme, you should let me know who wrote code line 1.",
                            "You should not alert me about direct conflict.",
                            "Sayme, you should check File1.py if this is gonna make a conflict.",
                            "You should tell me user1's working status.",
                            "You should announce that don't touch File1.py to conflict detect channel.",
                            "You have to send message to User2 that I will check and solve the confilct.",
                            "You would tell me how I can solve the conflict in File1.py"]
desire_sentence_list = ["I want to ignore any alarm about File1.py.", "I want to lock File1.py.",
                        "I want to know who wrote def1 in File1.py.", "I don't want you to alert about direct conflict",
                        "I want to know that this is gonna make a conflict in File1.py.",
                        "I want to know user1's working status.",
                        "I want to send the message in conflict detector channel that don't modify File1.py.",
                        "I want to send a direct message to user1 that don't modify File1.py.",
                        "I want to get recommendation how I can solve the conflict in File1.py."]


def intent_classifier(sentence):
    sentence_type = require_something_sentence(sentence)

    # Question
    if sentence_type == 1:
        user_input = nlp(sentence)
        max = 0
        for idx in range(0, len(question_sentence_list)):
            sample_input = nlp(question_sentence_list[idx])
            rate = user_input.similarity(sample_input)
            if rate > max and rate > 0.85:
                max_idx = idx + 1
                max = rate
        return max_idx

    # Command
    elif sentence_type == 2:
        user_input = nlp(sentence)
        max = 0
        for idx in range(0, len(command_sentence_list)):
            sample_input = nlp(command_sentence_list[idx])
            rate = user_input.similarity(sample_input)
            if rate > max and rate > 0.85:
                max_idx = idx + 1
                max = rate
        return max_idx

    # Suggestion
    elif sentence_type == 3:
        user_input = nlp(sentence)
        max = 0
        for idx in range(0, len(suggestion_sentence_list)):
            sample_input = nlp(suggestion_sentence_list[idx])
            rate = user_input.similarity(sample_input)
            if rate > max and rate > 0.85:
                max_idx = idx + 1
                max = rate
        return max_idx
    # Desire
    elif sentence_type == 4:
        user_input = nlp(sentence)
        max = 0
        for idx in range(0, len(desire_sentence_list)):
            sample_input = nlp(desire_sentence_list[idx])
            rate = user_input.similarity(sample_input)
            if rate > max and rate > 0.85:
                max_idx = idx + 1
                max = rate
        return max_idx
    else:
        return 10

#
# def extract_attention_word(sentence):
#     #work_db = work_database()
#     intent_type = intent_classifier(sentence)
#     print(intent_type)
#     if intent_type == 1:
#         file_list = project_parser("UCNLP", "conflict-detector")["file"]
#         result_file_list = []
#         for fl in file_list:
#             remove_list = []
#             approve_set = ()
#             r = fl.split("/")[-1]
#             result_file_list.append(" "+r)
#         for rfl in result_file_list:
#             if rfl in sentence:
#                 if 'not' in sentence or 'nt' in sentence or 'un' in sentence:
#                     remove_list.append(file_list[result_file_list.index(rfl)])
#                 else:
#                     approve_set.add(file_list[result_file_list.index(rfl)])
#
#         if len(remove_list) > 0:
#             #work_db.remove_approved_list("lsebb1007", remove_list)
#             print(remove_list)
#         elif len(approve_set) > 0:
#             #work_db.add_approved_list("lsebb1007", approve_set)
#             print(approve_set)
#         pass
#
#     elif intent_type == 2:
#         pass
#     elif intent_type == 3:
#
#         pass
#     elif intent_type == 4:
#         pass
#     elif intent_type == 5:
#         pass
#     elif intent_type == 6:
#         pass
#     elif intent_type == 7:
#         pass
#     elif intent_type == 8:
#         pass
#     elif intent_type == 9:
#         pass
    #work_db.close()
