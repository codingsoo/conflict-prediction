import spacy

from chat_bot_server_dir.user_intent_classifier.sentence_type_finder import require_something_sentence

# You can download this file : https://spacy.io/usage/vectors-similarity
nlp = spacy.load('C:\\Users\\learn\\PycharmProjects\\conflict-detector2\\venv\\Lib\\site-packages\\en_core_web_lg\\en_core_web_lg-2.0.0')

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

question_sentence_list = []