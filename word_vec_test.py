import spacy

# https://spacy.io/usage/vectors-similarity


nlp = spacy.load('/Users/Kathryn/Documents/GitHub/conflict-detector/venv/lib/python3.7/site-packages/en_core_web_lg/en_core_web_lg-2.0.0')

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


question_sentence_list = ["Can you not notify me about hello.py?", "Could you please lock hello.py?", "Do you know who wrote line14?", "Can you not notify me about indirect conflict?", "Do you think this is gonna make a conflict?", "Can you tell me user2’s working status?", "Can you tell everyone that I'm working on File1.py?", "Can you chat to User2 that I will check and solve the problem?", "How can I solve the conflict in File1.py?"]
command_sentence_list = ["Don’t alert me about File1.py again.", "Lock hello.py file.", "Tell me who wrote def1().", "Don't alert me about indirect conflict.", "Check File1.py whether it will make conflict or not.", "Give me User2’s working status.", "Tell everyone that I’m working on File1.py to conflict detect channel.", "Send user2 a message that I’m working on class1.", "Give me some recommendation about how to solve the conflict of File1.py."]
suggestion_sentence_list = ["You should not give me notification about File1.py", "You should lock File.py.", "Sayme, you should let me know who wrote code line 1.", "You should not alert me about direct conflict.", "Sayme, you should check File1.py if this is gonna make a conflict.", "You should tell me user1’s working status.", "You should announce that don’t touch File1.py to conflict detect channel.", "You have to send message to User2 that I will check and solve the confilct.", "You would tell me how I can solve the conflict in File1.py"]
desire_sentence_list = ["I want to ignore any alarm about File1.py.", "I want to lock File1.py.", "I would like to know who wrote def1 in File1.py.", "I don't want alarm about direct conflict", "I would like to know that this is gonna make a conflict in File1.py.", "I want to know user1’s working status.", "I hope to send the message in general channel that don’t modify File1.py.", "I wish you to send a direct message to user1 that don’t modify File1.py.", "I wish you to recommend how I can solve the conflict in File1.py." ]

sen = "I don't want to get notify about File.1.py"

for i in range(0,9):
    doc1 = nlp(sen)
    doc5 = nlp(desire_sentence_list[i])
    print(doc1.similarity(doc5))

# doc1 = nlp("Could you please lock hello.py?")
# doc2 = nlp("Lock hello.py file.")
# doc3 = nlp("You should lock File.py.")
# doc4 = nlp("I want to lock File1.py.")
# doc5 = nlp("Unlock hello.py file.")
#
#
# print(doc1.similarity(doc2))
# print(doc1.similarity(doc3))
# print(doc1.similarity(doc4))
# print(doc1.similarity(doc5))
# print(doc2.similarity(doc3))
# print(doc2.similarity(doc4))
# print(doc2.similarity(doc5))
# print(doc3.similarity(doc4))
# print(doc3.similarity(doc5))



# for token in tokens:
#     print(token.text, token.has_vector, token.vector_norm, token.is_oov)