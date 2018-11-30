#import nltk
from stanfordcorenlp import StanfordCoreNLP

#nltk.download('wordnet')

def sentence_preprocess(_sentence):

    # Change sentence to lower_case except slack code(<@ABCDEFGHI>) and file name(File.py)
    punc_list = ["!", "?", ",", ".", "’"]

    # Please preserve the order of elements in replace_list.
    replace_list = [(" please ", " "), (" hey ", " "), (" i think ", " "),
                    (" can't ", " can not "), (" won't ", " will not "), ("n't ", " not "),
                    (" do not have to ", " should not "),
                    (" have to ", " should "), (" ought to ", " should "), (" ought not to ", " should not "),
                    (" got to ", " should "), (" gotta ", " should "),
                    (" wanna ", " want to "),
                    ("'m ", " am "), ("'ve ", " have "), ("'re ", " are "),
                    (" where's ", " where is "), (" what's ", " what is "), (" who's ", " who is "), (" how's ", " how is "), (" why's ", " why is "),
                    (" the ", " "), (" a ", " "), (" an ", " ")]
    # can't -> can not, won't -> will not
    # shouldn't -> should not, wouldn't -> would not, couldn't -> could not , don't -> do not, haven't -> have not

    sentence = _sentence.lstrip("!,.? ").lower()

    for punc in punc_list:
        if punc == "’":
            sentence = sentence.replace(punc, "'")
        if punc != ".":
            sentence = sentence.replace(punc, " " + punc + " ")

    sentence = " " + sentence + " "

    for replace_tag in replace_list:
        sentence = sentence.replace(replace_tag[0], replace_tag[1])

    # Exception handling : Sentence with Sayme (ex : Sayme,.!? Sayme,?.! Could you help me?)
    # Extract all of "sayme", if the verb doesn't follow "sayme"
    sentence = sentence.lstrip("!.,? ")
    if sentence.startswith("sayme"):
        without_sayme_st = sentence.replace("sayme","").lstrip()
        count = 0
        for punc in punc_list:
            if not without_sayme_st.startswith(punc) and punc != "’":
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
            if word == "i":
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

def is_question(_sentence, pos_tag_list, nlp):
    sentence = (_sentence.rstrip(" .,!?") + " / ?").replace(" not ", " ", 1)
    print(sentence)
    parse_list = nlp.parse(sentence)
    print("parse_list", parse_list)
    if ("SBARQ" in parse_list or "SQ" in parse_list) and pos_tag_list[0][1] != "VB":
        return True
    else:
        for pos_tag in pos_tag_list:
            if pos_tag[0] == "how" or pos_tag[0] == "what":
                pos_idx = pos_tag_list.index((pos_tag[0], pos_tag[1]))
                if pos_tag_list[pos_idx + 1][0] == "about":
                    return True
    return False

def is_command(_sentence, nlp):
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


def is_suggestion(pos_tag_list):
    suggestion_noun_list = ["you", "sayme"]
    for pos_tag in pos_tag_list:
        if pos_tag[0] in suggestion_noun_list:
            pass
        elif pos_tag[1] == "MD":
            return True
        else:
            return False

def is_desire(pos_tag_list):
    ignore_pos_list = ["RB", ",", "!", "."]
    VPN_list = ["do", "am", "are", "is", "be"]
    desire_list = ["want", "hope", "wish", "desire", "need", "like", "love"]
    wonder_list = ["wonder", "curious", "aware", "conscious", "inquisitive", "interested", "questioning", "searching"]


    for pos_tag in pos_tag_list: # I should get @Sun's working status.
        # if pos_tag[0] == "I" or pos_tag[1] in ignore_pos_list:
        #     pass
        # elif pos_tag[0] in VPN_list and pos_tag[1] == "VBP":
        #     pass
        # elif pos_tag[1] == "MD" or pos_tag[0] in desire_list or pos_tag[0] in wonder_list:
        #     return True
        # else:
        #     return False
        if pos_tag[1] in ignore_pos_list:
            pass
        elif pos_tag[0] == "I":
            return True
        else:
            return False

def require_something_sentence(_sentence):
    nlp = StanfordCoreNLP('http://localhost', port=9000)
    sentence = sentence_preprocess(_sentence)
    pos_tag_list = nlp.pos_tag(sentence)

    # lemmatizer = nltk.WordNetLemmatizer()
    # for pos_tag in pos_tag_list:
        # if pos_tag[1] == "VB" or pos_tag[1] == "VBP" or pos_tag[1] == "VBG":
            # org_wrd = lemmatizer.lemmatize(pos_tag[0], pos ="v")
            # sentence = sentence.replace(" " + pos_tag[0] + " ", " " + org_wrd + " ")

    print("sentence", sentence)
    print("pos_tag_list", pos_tag_list)

    if is_question(sentence, pos_tag_list, nlp):
        for pos_tag in pos_tag_list:
            if pos_tag[1] == "MD" or pos_tag[0] == "do": # couldn't you do that?
                sentence = sentence.replace(" "+pos_tag[0]+" ", " can ", 1)
                pos_idx = pos_tag_list.index((pos_tag[0], pos_tag[1]))
                if pos_tag_list[pos_idx + 1][0] == "not":
                    sentence = sentence.replace(" not ", " ", 1)
                if pos_tag_list[pos_idx + 1][0] == "I" or pos_tag_list[pos_idx + 2][0] == "I":
                    sentence = sentence.replace(" I ", " you ", 1)
                break

        return 1, sentence

    elif is_command(sentence, nlp):
        return 2, sentence

    elif is_suggestion(pos_tag_list):
        for pos_tag in pos_tag_list:
            if pos_tag[1] == "MD":
                sentence = sentence.replace(pos_tag[0], "should", 1)
                break
        return 3, sentence

    elif is_desire(pos_tag_list):
        return 4, sentence

    else:
        return 5, sentence