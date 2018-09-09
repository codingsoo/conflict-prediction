import nltk
from stanfordcorenlp import StanfordCoreNLP

def sentence_preprocess(sentence):
    # User 이름, 파일명 제외하고는 전체 문장 소문자화 하기.
    extension_list = [".py", ".py.", ".md", ".md.", ".txt", ".txt.", ".json", ".json."]

    sentence = sentence.replace("’", "'")

    word_list = sentence.split()
    word_list[0] = word_list[0].lower().replace("sayme,", '')
    for word in word_list:
        len_word = len(word)
        # user name
        if word[0:2] == "@<" and (word[len_word-1] == ">" or word[len_word-3:len_word] == ">'s"):
            pass
        # file name
        elif word[len_word-3:len_word] in extension_list or word[len_word-4:len_word] in extension_list \
                or word[len_word-5:len_word] in extension_list or word[len_word-6:len_word] in extension_list:
            pass
        elif word.lower() == "i" or word.lower() == "i'm" or word.lower() == "i've":
            word_list[word_list.index(word)] = word[0].upper() + word[1:].lower()
        else:
            word_list[word_list.index(word)] = word.lower()

    sentence = ' '.join(word_list)
    # User 이름, 파일명 제외하고 전체 문장에서 replace하기.
    sentence = sentence.replace("please ", '')
    sentence = sentence.replace("i think ", '')
    sentence = sentence.replace("have to", "should")
    sentence = sentence.replace("don't have to", "shouldn't")
    sentence = sentence.replace("do not have to", "shouldn't")
    sentence = sentence.replace("n't ", " not ")
    sentence = sentence.replace("'m ", " am ")
    sentence = sentence.replace("'re ", " are ")
    sentence = sentence.replace("'ve ", " have ")

    return sentence

def is_command(_sentence):
    nlp = StanfordCoreNLP('http://localhost', port=9000)
    # sentence 제일 앞에 modal 추가
    sentence = "Must " + _sentence
    pos_tag_list = nlp.pos_tag(sentence)

    for pos_tag in pos_tag_list:
        if pos_tag[1] == "RB" or pos_tag[1] == "MD":
            pass
        elif (pos_tag[1] == "VB" and pos_tag[0] != "sayme") or pos_tag[1] == "VBP":
            return True
        else:
            return False

def is_desire(pos_tag_list):
    ignore_pos_list = ["RB", ",", "!", "."]
    VPN_list = ["do", "am", "are", "is", "be"]
    desire_list = ["want", "hope", "wish", "desire", "need", "like", "love"]
    wonder_list = ["wonder", "curious", "aware"]


    for pos_tag in pos_tag_list: # I should get @Sun's working status.
        if pos_tag[0] == "I" or pos_tag[1] in ignore_pos_list:
            pass
        elif pos_tag[0] in VPN_list and pos_tag[1] == "VBP":
            pass
        elif pos_tag[1] == "MD" or pos_tag[0] in desire_list or pos_tag[0] in wonder_list:
            return True
        else:
            return False

def is_suggestion(pos_tag_list):
    suggestion_noun_list = ["sayme", "you", ".", ","]
    for pos_tag in pos_tag_list:
        if pos_tag[0] in suggestion_noun_list:
            pass
        elif pos_tag[1] == "MD":
            return True
        else:
            return False

def is_question(parse_list, pos_tag_list):
    if "SBARQ" in parse_list or "SQ" in parse_list:
        return True
    elif (pos_tag_list[0][0] == "how" or pos_tag_list[0][0] == "what") and pos_tag_list[1][0] == "about":
        return True
    return False

def require_something_sentence(_sentence):
    nlp = StanfordCoreNLP('http://localhost', port=9000)
    sentence = sentence_preprocess(_sentence)
    pos_tag_list = nlp.pos_tag(sentence)
    parse_list = nlp.parse(sentence)

    if is_question(parse_list, pos_tag_list):
        if pos_tag_list[0][1] == "MD":
            sentence = sentence.replace(pos_tag_list[0][0], "can")
        return 1, sentence

    elif is_command(sentence):
        return 2, sentence

    elif is_suggestion(pos_tag_list):
        if pos_tag_list[1][1] == "MD":
            sentence = sentence.replace(pos_tag_list[1][0], "should")
        return 3, sentence

    elif is_desire(pos_tag_list):
        return 4, sentence

    else:
        return 5, sentence

