import nltk
from stanfordcorenlp import StanfordCoreNLP
import re

def sentence_preprocess(_sentence):
    # User 이름, 파일명 제외하고는 전체 문장 소문자화 하기.
    punc_list = {"!", "?", ",", ".", "’"}

    sentence = _sentence.lstrip("!,.? ").lower()

    for punc in punc_list:
        if punc != ".":
            sentence = sentence.replace(punc, " " + punc + " ")

    sentence = " " + sentence + " "
    # User 이름, 파일명 제외하고 전체 문장에서 replace하기.
    sentence = sentence.replace(" please ", ' ')
    sentence = sentence.replace(" hey ", ' ')
    sentence = sentence.replace(" i think ", ' ')
    sentence = sentence.replace(" have to ", " should ")
    sentence = sentence.replace("n't ", " not ")
    sentence = sentence.replace(" don't have to ", " should not ")
    sentence = sentence.replace(" do not have to ", " should not ")
    sentence = sentence.replace("'m ", " am ")
    sentence = sentence.replace("'re ", " are ")
    sentence = sentence.replace("'ve ", " have ")

    # Sayme preprocessing
    # sayme 다음에 동사가 나오지 않을 경우 sayme 다 빼냄. (ex : Sayme,.!? Sayme,?.! Could you help me?)
    sentence = sentence.lstrip("!.,? ")
    if sentence.startswith("sayme"):
        without_sayme_st = sentence.replace("sayme","").lstrip()
        count = 0
        for punc in punc_list:
            if without_sayme_st.startswith(punc) == False and punc != "’":
                count = count + 1
        if count != 4:
            sentence = without_sayme_st.lstrip("!?,. ")


    word_list = sentence.split()
    for word in word_list:
        word_idx = word_list.index(word)
        if word.find("<@") != -1 and word[word.find("<@") + 11] == ">":
            modified_word = word.upper()
        elif ".py" in word or ".md" in word or ".txt" in word or ".json" in word:
            file_idx = _sentence.lower().find(word)
            modified_word = _sentence[file_idx:file_idx + len(word)]
        else:
            if word == "i" or word == "i'm" or word == "i've":
                modified_word = word[0].upper() + word[1:]
            elif word == "sayme":
                modified_word = "you"
            else:
                modified_word = word.replace(".", " .") #for detecting word
        word_list[word_idx] = modified_word

    sentence = ' '.join(word_list)

    sentence = sentence.strip()
    sentence = " " + sentence + " "

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
    suggestion_noun_list = ["you", "sayme"]
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
    else:
        for pos_tag in pos_tag_list:
            if pos_tag[0] == "how" or pos_tag[0] == "what":
                pass
            elif pos_tag[0] == "about":
                return True

                # pos_idx = pos_tag_list.index((pos_tag[0], pos_tag[1]))
                # if pos_tag_list[pos_idx + 1][0] == "about":
                #     return True
    return False

def require_something_sentence(_sentence):
    nlp = StanfordCoreNLP('http://localhost', port=9000)
    sentence = sentence_preprocess(_sentence)
    pos_tag_list = nlp.pos_tag(sentence)
    parse_list = nlp.parse(sentence)

    print("sentence", sentence)
    print("pos_tag_list", pos_tag_list)
    print("parse_list", parse_list)

    if is_question(parse_list, pos_tag_list):
        for pos_tag in pos_tag_list:
            if pos_tag[1] == "MD":
                sentence = sentence.replace(pos_tag[0], "can")
                break
        return 1, sentence

    elif is_command(sentence):
        return 2, sentence

    elif is_suggestion(pos_tag_list):
        for pos_tag in pos_tag_list:
            if pos_tag[1] == "MD":
                sentence = sentence.replace(pos_tag[0], "should")
                break
        return 3, sentence

    elif is_desire(pos_tag_list):
        return 4, sentence

    else:
        return 5, sentence

